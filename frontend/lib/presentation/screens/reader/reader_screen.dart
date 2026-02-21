import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:go_router/go_router.dart';
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../core/web_audio_player.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/theme/colors.dart';
import '../../../core/constants.dart';
import '../../../core/l10n/app_localizations.dart';
import '../../../domain/providers/book_provider.dart';
import '../../../domain/models/book.dart';
import 'native_page_renderer.dart';

// ─── Audio Playback State ───
enum PlaybackState { idle, playing, paused }

class ReaderScreen extends ConsumerStatefulWidget {
  final int initialPage;
  const ReaderScreen({super.key, required this.initialPage});

  @override
  ConsumerState<ReaderScreen> createState() => _ReaderScreenState();
}

class _ReaderScreenState extends ConsumerState<ReaderScreen> {
  late PageController _pageController;
  final WebAudioPlayer _webAudio = WebAudioPlayer();

  int _currentPage = 1;
  bool _showOverlay = true;

  // Audio playback
  PlaybackState _playbackState = PlaybackState.idle;
  int _currentUnitIndex = 0;
  int? _activeUnitId;
  List<TextUnit> _currentPageUnits = [];
  List<TextUnit> _playSectionUnits = [];
  List<String> _currentPageAudioUrls = [];
  int _currentAudioIndex = 0;
  bool _isPageAudioMode = false;
  bool _isAutoAdvancing = false;

  @override
  void initState() {
    super.initState();
    _currentPage = widget.initialPage;
    _pageController = PageController(initialPage: widget.initialPage - 1);
    SharedPreferences.getInstance().then((prefs) {
      prefs.setInt(AppConstants.keyLastReadPage, widget.initialPage);
    });

    // Audio tugaganda — keyingisiga o'tish
    _webAudio.onCompleted = _onAudioCompleted;
  }

  void _onAudioCompleted() {
    if (_playbackState != PlaybackState.playing) return;
    if (_isPageAudioMode) {
      _advancePageAudio();
    } else if (_playSectionUnits.isNotEmpty) {
      _advanceSectionUnit();
    } else {
      _advanceToNextUnit();
    }
  }

  @override
  void dispose() {
    _pageController.dispose();
    _webAudio.dispose();
    super.dispose();
  }

  // ─── Called when page data loads or page changes ───
  void _updatePageUnits(List<TextUnit> units) {
    if (!mounted) return;
    _currentPageUnits = units
      ..sort((a, b) => a.sortOrder.compareTo(b.sortOrder));
  }

  // ─── Called when page audio URLs are loaded ───
  void _updatePageAudio(List<String> audioUrls) {
    if (!mounted) return;
    _currentPageAudioUrls = audioUrls;
  }

  // ─── PLAY: Start audio playback ───
  Future<void> _startPlaying() async {
    // Agar unitlarda alohida audio segment bo'lsa, unit-by-unit play
    final hasUnitAudio = _currentPageUnits.any(
      (u) => u.audioSegmentUrl != null && u.audioSegmentUrl!.isNotEmpty,
    );

    if (hasUnitAudio && _currentPageUnits.isNotEmpty) {
      // Unit-by-unit playback (har bir unit o'z segmentini play qiladi)
      _isPageAudioMode = false;
      _playSectionUnits = [];
      setState(() => _playbackState = PlaybackState.playing);
      await _playCurrentUnit();
    } else if (_currentPageAudioUrls.isNotEmpty) {
      // Fallback: sahifa-darajasidagi audio
      _isPageAudioMode = true;
      _currentAudioIndex = 0;
      setState(() => _playbackState = PlaybackState.playing);
      await _playCurrentPageAudio();
    } else if (_currentPageUnits.isNotEmpty) {
      // Fallback: unit-by-unit (audio'siz highlight qilish)
      _isPageAudioMode = false;
      _playSectionUnits = [];
      setState(() => _playbackState = PlaybackState.playing);
      await _playCurrentUnit();
    }
  }

  // ─── Play current page audio file ───
  Future<void> _playCurrentPageAudio() async {
    if (_currentAudioIndex >= _currentPageAudioUrls.length) {
      setState(() {
        _playbackState = PlaybackState.idle;
        _activeUnitId = null;
        _isPageAudioMode = false;
        _currentAudioIndex = 0;
      });
      return;
    }

    final url = _currentPageAudioUrls[_currentAudioIndex];
    try {
      await _webAudio.playUrl(url);
    } catch (e) {
      debugPrint('Page audio error: $e');
      _advancePageAudio();
    }
  }

  // ─── Advance to next page audio ───
  void _advancePageAudio() {
    if (_playbackState != PlaybackState.playing) return;
    _currentAudioIndex++;
    _playCurrentPageAudio();
  }

  // ─── PLAY SECTION: Play only units in a specific section ───
  Future<void> _playSectionByIds(List<int> unitIds) async {
    if (_currentPageUnits.isEmpty || unitIds.isEmpty) return;

    // Filter current page units to only those in the section
    _playSectionUnits = _currentPageUnits
        .where((u) => unitIds.contains(u.id))
        .toList();
    if (_playSectionUnits.isEmpty) return;

    _currentUnitIndex = 0;
    setState(() => _playbackState = PlaybackState.playing);
    await _playSectionUnit();
  }

  // ─── Play the current section unit ───
  Future<void> _playSectionUnit() async {
    if (_currentUnitIndex >= _playSectionUnits.length) {
      setState(() {
        _playbackState = PlaybackState.idle;
        _activeUnitId = null;
        _currentUnitIndex = 0;
        _playSectionUnits = [];
      });
      return;
    }

    final unit = _playSectionUnits[_currentUnitIndex];
    if (!mounted) return;
    setState(() => _activeUnitId = unit.id);

    if (unit.audioSegmentUrl != null && unit.audioSegmentUrl!.isNotEmpty) {
      try {
        await _webAudio.playUrl(unit.audioSegmentUrl!);
      } catch (e) {
        debugPrint('Section audio error: $e');
        _advanceSectionUnit();
      }
    } else {
      await Future.delayed(const Duration(milliseconds: 400));
      if (_playbackState == PlaybackState.playing) {
        _advanceSectionUnit();
      }
    }
  }

  // ─── Advance to next unit within section ───
  void _advanceSectionUnit() {
    if (_playbackState != PlaybackState.playing) return;
    _currentUnitIndex++;
    _playSectionUnit();
  }

  // ─── Play the current unit's audio ───
  Future<void> _playCurrentUnit() async {
    if (_currentUnitIndex >= _currentPageUnits.length) {
      _autoAdvanceToNextPage();
      return;
    }

    final unit = _currentPageUnits[_currentUnitIndex];
    if (!mounted) return;
    setState(() => _activeUnitId = unit.id);

    if (unit.audioSegmentUrl != null && unit.audioSegmentUrl!.isNotEmpty) {
      try {
        await _webAudio.playUrl(unit.audioSegmentUrl!);
      } catch (e) {
        debugPrint('Audio error: $e');
        _advanceToNextUnit();
      }
    } else {
      await Future.delayed(const Duration(milliseconds: 400));
      if (_playbackState == PlaybackState.playing) {
        _advanceToNextUnit();
      }
    }
  }

  // ─── Advance to next unit ───
  void _advanceToNextUnit() {
    if (_playbackState != PlaybackState.playing) return;

    _currentUnitIndex++;
    if (_currentUnitIndex >= _currentPageUnits.length) {
      _autoAdvanceToNextPage();
    } else {
      _playCurrentUnit();
    }
  }

  // ─── Auto-advance to next page ───
  Future<void> _autoAdvanceToNextPage() async {
    final totalPages = ref.read(bookProvider).valueOrNull?.totalPages ?? 16;
    if (_currentPage >= totalPages) {
      // Book finished
      setState(() {
        _playbackState = PlaybackState.idle;
        _activeUnitId = null;
        _currentUnitIndex = 0;
      });
      return;
    }

    _isAutoAdvancing = true;
    _currentUnitIndex = 0;

    // Animate to next page
    await _pageController.nextPage(
      duration: const Duration(milliseconds: 400),
      curve: Curves.easeInOut,
    );

    // Wait for page data to load
    await Future.delayed(const Duration(milliseconds: 800));

    if (_playbackState == PlaybackState.playing && mounted) {
      _isAutoAdvancing = false;
      await _playCurrentUnit();
    }
  }

  // ─── PAUSE ───
  void _pause() {
    _webAudio.pause();
    setState(() => _playbackState = PlaybackState.paused);
  }

  // ─── RESUME ───
  Future<void> _resume() async {
    setState(() => _playbackState = PlaybackState.playing);

    if (_webAudio.isPaused) {
      _webAudio.resume();
    } else if (_isPageAudioMode) {
      await _playCurrentPageAudio();
    } else {
      await _playCurrentUnit();
    }
  }

  // ─── STOP ───
  void _stop() {
    _webAudio.stop();
    setState(() {
      _playbackState = PlaybackState.idle;
      _activeUnitId = null;
      _currentUnitIndex = 0;
      _currentAudioIndex = 0;
      _isPageAudioMode = false;
      _playSectionUnits = [];
    });
  }

  // ─── TAP on a specific unit ───
  Future<void> _tapUnit(TextUnit unit) async {
    _webAudio.stop(); // Avvalgisini to'xtatish

    setState(() {
      _activeUnitId = unit.id;
      _isPageAudioMode = false;
      final idx = _currentPageUnits.indexWhere((u) => u.id == unit.id);
      if (idx >= 0) _currentUnitIndex = idx;
    });

    if (unit.audioSegmentUrl != null && unit.audioSegmentUrl!.isNotEmpty) {
      try {
        await _webAudio.playUrl(unit.audioSegmentUrl!);
      } catch (e) {
        debugPrint('Audio error: $e');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final totalPages = ref.watch(bookProvider).valueOrNull?.totalPages ?? 16;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: Stack(
        children: [
          // ═══ Page viewer ═══
          PageView.builder(
            controller: _pageController,
            itemCount: totalPages,
            physics: _playbackState == PlaybackState.playing
                ? const NeverScrollableScrollPhysics()
                : null,
            onPageChanged: (index) {
              final newPage = index + 1;
              setState(() {
                _currentPage = newPage;
                if (!_isAutoAdvancing) {
                  _currentUnitIndex = 0;
                  _activeUnitId = null;
                }
              });
              // Sync browser URL without triggering navigation/rebuild
              if (kIsWeb) {
                html.window.history.replaceState(null, '', '#/reader/$newPage');
              }
              // Save last read page
              SharedPreferences.getInstance().then((prefs) {
                prefs.setInt(AppConstants.keyLastReadPage, newPage);
              });
            },
            itemBuilder: (context, index) {
              final pageNumber = index + 1;
              return _PageView(
                pageNumber: pageNumber,
                onUnitTap: _tapUnit,
                activeUnitId: _activeUnitId,
                onBackgroundTap: () {
                  setState(() => _showOverlay = !_showOverlay);
                },
                onUnitsLoaded: (units) {
                  if (pageNumber == _currentPage) {
                    _updatePageUnits(units);
                  }
                },
                onAudioUrlsLoaded: (audioUrls) {
                  if (pageNumber == _currentPage) {
                    _updatePageAudio(audioUrls);
                  }
                },
                onSectionPlay: _playSectionByIds,
              );
            },
          ),

          // ═══ Top overlay — page title ═══
          if (_showOverlay)
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: Container(
                padding: EdgeInsets.only(
                  top: MediaQuery.of(context).padding.top + 8,
                  left: 8,
                  right: 16,
                  bottom: 8,
                ),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Theme.of(context).scaffoldBackgroundColor,
                      Theme.of(context)
                          .scaffoldBackgroundColor
                          .withValues(alpha: 0),
                    ],
                  ),
                ),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_rounded),
                      onPressed: () {
                        _stop();
                        context.pop();
                      },
                    ),
                    Expanded(
                      child: Text(
                        AppLocalizations.of(context)?.pageOf(_currentPage, totalPages) ?? 'Sahifa $_currentPage / $totalPages',
                        style: Theme.of(context).textTheme.titleMedium,
                        textAlign: TextAlign.center,
                      ),
                    ),
                    const SizedBox(width: 48),
                  ],
                ),
              ),
            ),

          // ═══ Bottom Audio Bar ═══
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: _AudioBar(
              playbackState: _playbackState,
              currentUnitIndex: _currentUnitIndex,
              totalUnits: _currentPageUnits.length,
              currentPage: _currentPage,
              totalPages: totalPages,
              isPageAudioMode: _isPageAudioMode,
              currentAudioIndex: _currentAudioIndex,
              totalAudioTracks: _currentPageAudioUrls.length,
              onPlay: () {
                if (_playbackState == PlaybackState.paused) {
                  _resume();
                } else {
                  _startPlaying();
                }
              },
              onPause: _pause,
              onStop: _stop,
              onPageSliderChanged: (page) {
                _stop();
                _pageController.jumpToPage(page - 1);
              },
            ),
          ),
        ],
      ),
    );
  }
}

// ════════════════════════════════════════════════════════
// AUDIO BAR — Premium bottom controls
// ════════════════════════════════════════════════════════

class _AudioBar extends StatelessWidget {
  final PlaybackState playbackState;
  final int currentUnitIndex;
  final int totalUnits;
  final int currentPage;
  final int totalPages;
  final bool isPageAudioMode;
  final int currentAudioIndex;
  final int totalAudioTracks;
  final VoidCallback onPlay;
  final VoidCallback onPause;
  final VoidCallback onStop;
  final ValueChanged<int> onPageSliderChanged;

  const _AudioBar({
    required this.playbackState,
    required this.currentUnitIndex,
    required this.totalUnits,
    required this.currentPage,
    required this.totalPages,
    this.isPageAudioMode = false,
    this.currentAudioIndex = 0,
    this.totalAudioTracks = 0,
    required this.onPlay,
    required this.onPause,
    required this.onStop,
    required this.onPageSliderChanged,
  });

  @override
  Widget build(BuildContext context) {
    final bottomPadding = MediaQuery.of(context).padding.bottom;
    final isPlaying = playbackState == PlaybackState.playing;
    final isPaused = playbackState == PlaybackState.paused;
    final isActive = isPlaying || isPaused;

    return Container(
      padding: EdgeInsets.only(
        bottom: bottomPadding + 8,
        top: 12,
        left: 16,
        right: 16,
      ),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.bottomCenter,
          end: Alignment.topCenter,
          colors: [
            Theme.of(context).scaffoldBackgroundColor,
            Theme.of(context).scaffoldBackgroundColor.withValues(alpha: 0.95),
            Theme.of(context).scaffoldBackgroundColor.withValues(alpha: 0),
          ],
          stops: const [0.0, 0.7, 1.0],
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // ── Track/Unit progress (only when active) ──
          if (isActive)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Column(
                children: [
                  // Progress bar
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: isPageAudioMode && totalAudioTracks > 0
                          ? (currentAudioIndex + 1) / totalAudioTracks
                          : totalUnits > 0
                              ? (currentUnitIndex + 1) / totalUnits
                              : 0,
                      backgroundColor: AppColors.primary.withValues(alpha: 0.12),
                      valueColor: AlwaysStoppedAnimation<Color>(
                        AppColors.primary.withValues(alpha: 0.7),
                      ),
                      minHeight: 3,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    isPageAudioMode
                        ? '🔊 ${currentAudioIndex + 1} / $totalAudioTracks'
                        : '${currentUnitIndex + 1} / $totalUnits',
                    style: TextStyle(
                      fontSize: 11,
                      color: AppColors.primary.withValues(alpha: 0.6),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),

          // ── Controls row ──
          Row(
            children: [
              // Page number
              Text(
                '$currentPage',
                style: Theme.of(context).textTheme.bodySmall,
              ),

              // Page slider
              Expanded(
                child: SliderTheme(
                  data: SliderTheme.of(context).copyWith(
                    trackHeight: 3,
                    thumbShape: const RoundSliderThumbShape(
                      enabledThumbRadius: 7,
                    ),
                    overlayShape: const RoundSliderOverlayShape(
                      overlayRadius: 14,
                    ),
                    activeTrackColor: AppColors.primary,
                    inactiveTrackColor: AppColors.primary.withValues(alpha: 0.15),
                    thumbColor: AppColors.primary,
                    overlayColor: AppColors.primary.withValues(alpha: 0.12),
                  ),
                  child: Slider(
                    value: currentPage.toDouble(),
                    min: 1,
                    max: totalPages.toDouble(),
                    divisions: totalPages > 1 ? totalPages - 1 : 1,
                    onChanged: (val) {
                      onPageSliderChanged(val.round());
                    },
                  ),
                ),
              ),

              Text(
                '$totalPages',
                style: Theme.of(context).textTheme.bodySmall,
              ),

              const SizedBox(width: 12),

              // ── Audio control buttons ──
              _ControlButton(
                icon: isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
                isPrimary: true,
                isActive: isActive,
                onTap: isPlaying ? onPause : onPlay,
                size: 44,
              ),
              const SizedBox(width: 8),
              AnimatedOpacity(
                opacity: isActive ? 1.0 : 0.4,
                duration: const Duration(milliseconds: 200),
                child: _ControlButton(
                  icon: Icons.stop_rounded,
                  isPrimary: false,
                  isActive: isActive,
                  onTap: isActive ? onStop : null,
                  size: 36,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ── Control Button ──
class _ControlButton extends StatefulWidget {
  final IconData icon;
  final bool isPrimary;
  final bool isActive;
  final VoidCallback? onTap;
  final double size;

  const _ControlButton({
    required this.icon,
    required this.isPrimary,
    required this.isActive,
    this.onTap,
    required this.size,
  });

  @override
  State<_ControlButton> createState() => _ControlButtonState();
}

class _ControlButtonState extends State<_ControlButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _scaleController;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _scaleController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
      lowerBound: 0.9,
      upperBound: 1.0,
      value: 1.0,
    );
  }

  @override
  void dispose() {
    _scaleController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) {
        _scaleController.reverse();
        setState(() => _isPressed = true);
      },
      onTapUp: (_) {
        _scaleController.forward();
        setState(() => _isPressed = false);
        widget.onTap?.call();
      },
      onTapCancel: () {
        _scaleController.forward();
        setState(() => _isPressed = false);
      },
      child: AnimatedBuilder(
        animation: _scaleController,
        builder: (context, child) => Transform.scale(
          scale: _scaleController.value,
          child: child,
        ),
        child: Container(
          width: widget.size,
          height: widget.size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: widget.isPrimary
                ? AppColors.primary
                : AppColors.primary.withValues(alpha: 0.12),
            boxShadow: widget.isPrimary && widget.isActive
                ? [
                    BoxShadow(
                      color: AppColors.primary.withValues(alpha: 0.3),
                      blurRadius: 12,
                      spreadRadius: 2,
                    ),
                  ]
                : [],
          ),
          child: Icon(
            widget.icon,
            color: widget.isPrimary ? Colors.white : AppColors.primary,
            size: widget.size * 0.55,
          ),
        ),
      ),
    );
  }
}

// ════════════════════════════════════════════════════════
// PAGE VIEW — Renders a single page
// ════════════════════════════════════════════════════════

class _PageView extends ConsumerWidget {
  final int pageNumber;
  final Function(TextUnit) onUnitTap;
  final int? activeUnitId;
  final VoidCallback onBackgroundTap;
  final Function(List<TextUnit>) onUnitsLoaded;
  final Function(List<String>) onAudioUrlsLoaded;
  final Function(List<int>)? onSectionPlay;

  const _PageView({
    required this.pageNumber,
    required this.onUnitTap,
    this.activeUnitId,
    required this.onBackgroundTap,
    required this.onUnitsLoaded,
    required this.onAudioUrlsLoaded,
    this.onSectionPlay,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pageAsync = ref.watch(pageDetailProvider(pageNumber));

    return pageAsync.when(
      loading: () => const Center(
        child: CircularProgressIndicator(color: AppColors.primary),
      ),
      error: (err, _) => Center(
        child: Text('${AppLocalizations.of(context)?.error ?? 'Xatolik'}: $err',
            style: const TextStyle(color: AppColors.error)),
      ),
      data: (page) {
        if (page == null) {
          return Center(child: Text(AppLocalizations.of(context)?.pageNotFound ?? 'Sahifa topilmadi'));
        }

        // Notify parent about units for audio playback
        WidgetsBinding.instance.addPostFrameCallback((_) {
          onUnitsLoaded(page.textUnits);
          onAudioUrlsLoaded(page.audioUrls);
        });

        // === ALWAYS USE NATIVE RENDERER when text_units exist or page 1 (cover) ===
        if (page.textUnits.isNotEmpty || page.pageNumber == 1) {
          return GestureDetector(
            onTap: onBackgroundTap,
            child: InteractiveViewer(
              minScale: 1.0,
              maxScale: 4.0,
              child: NativePageRenderer(
                page: page,
                onUnitTap: onUnitTap,
                activeUnitId: activeUnitId,
                onSectionPlay: onSectionPlay,
              ),
            ),
          );
        }

        // === FALLBACK: Image-only for pages without text_units ===
        return GestureDetector(
          onTap: onBackgroundTap,
          child: InteractiveViewer(
            minScale: 1.0,
            maxScale: 4.0,
            child: page.imageUrl != null
                ? CachedNetworkImage(
                    imageUrl: page.imageUrl!,
                    fit: BoxFit.contain,
                    placeholder: (_, __) => Container(
                      color: Theme.of(context).scaffoldBackgroundColor,
                      child: const Center(
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                    ),
                    errorWidget: (_, __, ___) => Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.broken_image_rounded, size: 48),
                          const SizedBox(height: 8),
                          Text(AppLocalizations.of(context)?.imageLoadFailed ?? 'Rasm yuklanmadi',
                              style: Theme.of(context).textTheme.bodySmall),
                        ],
                      ),
                    ),
                  )
                : Center(child: Text(AppLocalizations.of(context)?.pageNotFound ?? 'Sahifa topilmadi')),
          ),
        );
      },
    );
  }
}
