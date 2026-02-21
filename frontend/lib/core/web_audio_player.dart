/// Web-specific audio player using JavaScript interop.
/// dart:html AudioElement Flutter web compile'da to'g'ri ishlamasligi mumkin,
/// shuning uchun to'g'ridan-to'g'ri JavaScript chaqiramiz.
library;

// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'dart:js' as js;
import 'package:flutter/foundation.dart';

class WebAudioPlayer {
  /// Callback — audio tugaganda chaqiriladi
  VoidCallback? onCompleted;

  /// Stop current audio and play new URL
  Future<void> playUrl(String url) async {
    // JavaScript orqali to'g'ridan-to'g'ri play qilish
    // Bu Flutter web interop muammolarini chetlab o'tadi
    js.context.callMethod('eval', ['''
      (function() {
        // Avvalgisini to'xtatish
        if (window.__muallimi_audio) {
          window.__muallimi_audio.pause();
          window.__muallimi_audio.src = '';
          window.__muallimi_audio = null;
        }
        // Yangi audio yaratish
        var a = new Audio("$url");
        a.play().catch(function(e) { console.log("Audio play error:", e); });
        a.onended = function() {
          window.__muallimi_audio = null;
          if (window.__muallimi_onended) {
            window.__muallimi_onended();
          }
        };
        window.__muallimi_audio = a;
      })();
    ''']);

    // Dart callback'ni JS ga ulash
    js.context['__muallimi_onended'] = js.allowInterop(() {
      onCompleted?.call();
    });
  }

  /// Pause
  void pause() {
    js.context.callMethod('eval', ['''
      if (window.__muallimi_audio) window.__muallimi_audio.pause();
    ''']);
  }

  /// Resume
  void resume() {
    js.context.callMethod('eval', ['''
      if (window.__muallimi_audio) window.__muallimi_audio.play();
    ''']);
  }

  /// Stop and clean up
  void stop() {
    js.context.callMethod('eval', ['''
      if (window.__muallimi_audio) {
        window.__muallimi_audio.pause();
        window.__muallimi_audio.src = '';
        window.__muallimi_audio = null;
      }
    ''']);
  }

  /// Is playing?
  bool get isPlaying {
    final result = js.context.callMethod('eval', ['''
      (window.__muallimi_audio && !window.__muallimi_audio.paused && !window.__muallimi_audio.ended) ? true : false
    ''']);
    return result == true;
  }

  /// Is paused?
  bool get isPaused {
    final result = js.context.callMethod('eval', ['''
      (window.__muallimi_audio && window.__muallimi_audio.paused && !window.__muallimi_audio.ended) ? true : false
    ''']);
    return result == true;
  }

  void dispose() {
    stop();
    onCompleted = null;
    js.context['__muallimi_onended'] = null;
  }
}
