/// Web-specific audio player using dart:html AudioElement.
/// just_audio webda setUrl to'g'ri ishlamaydi, shuning uchun
/// to'g'ridan-to'g'ri HTML5 Audio API ishlatamiz.
library;

// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'dart:async';
import 'package:flutter/foundation.dart';

class WebAudioPlayer {
  html.AudioElement? _audio;
  StreamSubscription? _endedSub;
  StreamSubscription? _errorSub;

  /// Callback — audio tugaganda chaqiriladi
  VoidCallback? onCompleted;

  /// Hozirgi URL
  String? _currentUrl;

  /// Yangi URL ni o'rnatib, ijro qilish
  Future<void> playUrl(String url) async {
    // Eski audio'ni to'xtatish va tozalash
    stop();

    _currentUrl = url;
    _audio = html.AudioElement(url);
    _audio!.preload = 'auto';

    // Completion callback
    _endedSub = _audio!.onEnded.listen((_) {
      onCompleted?.call();
    });

    _errorSub = _audio!.onError.listen((e) {
      debugPrint('WebAudioPlayer error: $e');
    });

    try {
      await _audio!.play();
    } catch (e) {
      debugPrint('WebAudioPlayer play error: $e');
    }
  }

  /// Pauzaga qo'yish
  void pause() {
    _audio?.pause();
  }

  /// Davom ettirish (pauzadan)
  void resume() {
    _audio?.play();
  }

  /// To'xtatish va tozalash
  void stop() {
    _endedSub?.cancel();
    _errorSub?.cancel();
    _endedSub = null;
    _errorSub = null;

    if (_audio != null) {
      _audio!.pause();
      _audio!.src = '';
      _audio!.load(); // Resurslarni bo'shatish
      _audio = null;
    }
    _currentUrl = null;
  }

  /// Ijro bo'lyaptimi?
  bool get isPlaying => _audio != null && !_audio!.paused && !_audio!.ended;

  /// Pauzadami?
  bool get isPaused => _audio != null && _audio!.paused && !_audio!.ended;

  void dispose() {
    stop();
    onCompleted = null;
  }
}
