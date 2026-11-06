import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'notifications.dart';
import 'screens/home_screen.dart';
import 'storage.dart';
import 'package:winter_core/winter_core.dart';

Future<void> main() => runWinterApp(repo: 'winter-expiry', appName: 'Просрочка', body: _main);

Future<void> _main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppStore.instance.load();
  await Notifier.init();
  Notifier.reschedule(AppStore.instance);
  runApp(WinterCrashBanner(child: const ExpiryApp()));
}

class ExpiryApp extends StatelessWidget {
  const ExpiryApp({super.key});

  @override
  Widget build(BuildContext context) {
    final scheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF7CC4FF),
      brightness: Brightness.dark,
    ).copyWith(surface: const Color(0xFF0F1B30));

    return MaterialApp(
      title: 'Просрочка',
      debugShowCheckedModeBanner: false,
      locale: const Locale('ru'),
      supportedLocales: const [Locale('ru'), Locale('pl'), Locale('en')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: scheme,
        scaffoldBackgroundColor: const Color(0xFF0A1322),
      ),
      home: const HomeScreen(),
    );
  }
}
