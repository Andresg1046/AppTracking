import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/auth_response.dart';
import '../models/login_request.dart';
import '../models/register_request.dart';
import '../models/register_response.dart';
import '../models/user.dart';

class AuthService {
  static const String baseUrl = 'http://192.168.1.130:8000'; // IP del servidor local
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String logoutEndpoint = '/auth/logout';
  static const String forgotPasswordEndpoint = '/auth/forgot-password';
  static const String resetPasswordEndpoint = '/auth/reset-password';
  static const String usersEndpoint = '/users';
  static const String healthEndpoint = '/health';

  // Headers por defecto
  static Map<String, String> get _defaultHeaders => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // Headers con token de autorización
  static Future<Map<String, String>> _getAuthHeaders() async {
    final token = await getStoredToken();
    final headers = Map<String, String>.from(_defaultHeaders);
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  // Almacenar tokens en SharedPreferences
  static Future<void> storeTokens(String accessToken, String refreshToken) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', accessToken);
    await prefs.setString('refresh_token', refreshToken);
  }

  // Obtener access token almacenado
  static Future<String?> getStoredToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  // Obtener refresh token almacenado
  static Future<String?> getStoredRefreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('refresh_token');
  }


  // Almacenar información del usuario
  static Future<void> storeUser(User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('user_data', jsonEncode(user.toJson()));
  }

  // Obtener información del usuario
  static Future<User?> getStoredUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userData = prefs.getString('user_data');
    if (userData != null) {
      return User.fromJson(jsonDecode(userData));
    }
    return null;
  }

  // Limpiar datos de autenticación
  static Future<void> clearAuthData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('user_data');
  }

  // Login
  static Future<AuthResponse> login(LoginRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl$loginEndpoint'),
        headers: _defaultHeaders,
        body: jsonEncode(request.toJson()),
      );

      if (response.statusCode == 200) {
        final authResponse = AuthResponse.fromJson(jsonDecode(response.body));
        
        // Almacenar tokens
        await storeTokens(authResponse.accessToken, authResponse.refreshToken);
        
        return authResponse;
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'Error en el login');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Registro
  static Future<RegisterResponse> register(RegisterRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl$registerEndpoint'),
        headers: _defaultHeaders,
        body: jsonEncode(request.toJson()),
      );

      if (response.statusCode == 200) {
        return RegisterResponse.fromJson(jsonDecode(response.body));
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'Error en el registro');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Logout
  static Future<void> logout() async {
    try {
      final token = await getStoredToken();
      if (token != null) {
        // Intentar hacer logout en el backend
        await http.post(
          Uri.parse('$baseUrl$logoutEndpoint'),
          headers: await _getAuthHeaders(),
        );
      }
    } catch (e) {
      // Ignorar errores de logout en el backend
      print('Error en logout del backend: $e');
    } finally {
      // Siempre limpiar datos locales
      await clearAuthData();
    }
  }

  // Verificar salud del backend
  static Future<Map<String, dynamic>?> healthCheck() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl$healthEndpoint'),
        headers: _defaultHeaders,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  // Obtener información del usuario actual desde almacenamiento local
  static Future<User?> getCurrentUser() async {
    return await getStoredUser();
  }

  // Verificar si el usuario está autenticado
  static Future<bool> isAuthenticated() async {
    final token = await getStoredToken();
    final user = await getStoredUser();
    return token != null && user != null;
  }

  // Solicitar restablecimiento de contraseña
  static Future<Map<String, dynamic>> forgotPassword(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl$forgotPasswordEndpoint'),
        headers: _defaultHeaders,
        body: jsonEncode({'email': email}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'Error al solicitar restablecimiento');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Restablecer contraseña
  static Future<Map<String, dynamic>> resetPassword({
    required String email,
    required String resetCode,
    required String newPassword,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl$resetPasswordEndpoint'),
        headers: _defaultHeaders,
        body: jsonEncode({
          'email': email,
          'reset_code': resetCode,
          'new_password': newPassword,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'Error al restablecer contraseña');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Obtener información del usuario actual desde el backend
  static Future<User?> getCurrentUserFromBackend() async {
    try {
      final token = await getStoredToken();
      if (token == null) return null;

      final response = await http.get(
        Uri.parse('$baseUrl$usersEndpoint/me'),
        headers: await _getAuthHeaders(),
      );

      if (response.statusCode == 200) {
        final userData = jsonDecode(response.body);
        final user = User.fromJson(userData);
        await storeUser(user); // Actualizar datos locales
        return user;
      }
      return null;
    } catch (e) {
      print('Error al obtener usuario del backend: $e');
      return null;
    }
  }
}
