import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeProvider with ChangeNotifier {
  static const String _themeKey = 'theme_mode';
  
  ThemeMode _themeMode = ThemeMode.system;
  
  ThemeMode get themeMode => _themeMode;
  
  bool get isDarkMode {
    if (_themeMode == ThemeMode.system) {
      return WidgetsBinding.instance.platformDispatcher.platformBrightness == Brightness.dark;
    }
    return _themeMode == ThemeMode.dark;
  }
  
  ThemeProvider() {
    _loadTheme();
  }
  
  Future<void> _loadTheme() async {
    final prefs = await SharedPreferences.getInstance();
    final themeIndex = prefs.getInt(_themeKey) ?? 0;
    _themeMode = ThemeMode.values[themeIndex];
    notifyListeners();
  }
  
  Future<void> setThemeMode(ThemeMode themeMode) async {
    _themeMode = themeMode;
    notifyListeners();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_themeKey, themeMode.index);
  }
  
  void toggleTheme() {
    if (_themeMode == ThemeMode.light) {
      setThemeMode(ThemeMode.dark);
    } else {
      setThemeMode(ThemeMode.light);
    }
  }
  
  // Colores para tema oscuro
  static const Color darkBackground = Color(0xFF0F1115);
  static const Color darkSurface = Color.fromARGB(255, 70, 76, 84);
  static const Color darkCard = Color(0xFF1A1F2E);
  static const Color darkPrimary = Color(0xFFEE4B93);
  static const Color darkSecondary = Color(0xFF2C2F3A);
  
  // Colores para tema claro
  static const Color lightBackground = Color(0xFFF5F5F5);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightCard = Color(0xFFF8F9FA);
  static const Color lightPrimary = Color(0xFF2196F3);
  static const Color lightSecondary = Color(0xFFE3F2FD);
  
  // Método para obtener colores según el tema actual
  Color getBackgroundColor(bool isDark) {
    return isDark ? darkBackground : lightBackground;
  }
  
  Color getSurfaceColor(bool isDark) {
    return isDark ? darkSurface : lightSurface;
  }
  
  Color getCardColor(bool isDark) {
    return isDark ? darkCard : lightCard;
  }
  
  Color getPrimaryColor(bool isDark) {
    return isDark ? darkPrimary : lightPrimary;
  }
  
  Color getSecondaryColor(bool isDark) {
    return isDark ? darkSecondary : lightSecondary;
  }
  
  Color getTextColor(bool isDark) {
    return isDark ? Colors.white : Colors.black87;
  }
  
  Color getSecondaryTextColor(bool isDark) {
    return isDark ? Colors.white70 : Colors.grey[600]!;
  }
}
