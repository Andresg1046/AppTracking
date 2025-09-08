import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';

class UserService {
  static const String baseUrl =
      'http://192.168.1.130:8000'; // IP del servidor local
  static const String usersEndpoint = '/users';
  static const String rolesEndpoint = '/roles';

  // Headers por defecto
  static Map<String, String> get _defaultHeaders => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // Headers con token de autorización
  static Future<Map<String, String>> _getAuthHeaders() async {
    final token = await _getStoredToken();
    final headers = Map<String, String>.from(_defaultHeaders);
    print('Token obtenido: ${token != null ? "SÍ" : "NO"}');
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
      print('Token enviado: ${token.substring(0, 20)}...');
    } else {
      print('ERROR: No hay token disponible');
    }
    return headers;
  }

  // Obtener token almacenado
  static Future<String?> _getStoredToken() async {
    // Importar SharedPreferences aquí para evitar dependencias circulares
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    print(
      'Token recuperado de SharedPreferences: ${token != null ? "SÍ" : "NO"}',
    );
    if (token != null) {
      print('Token completo: $token');
    }
    return token;
  }

  // Método de debug para verificar autenticación
  static Future<void> debugAuth() async {
    final token = await _getStoredToken();
    print('=== DEBUG AUTHENTICATION ===');
    print('Token disponible: ${token != null ? "SÍ" : "NO"}');
    if (token != null) {
      print('Token: $token');
    }

    // Probar endpoint de health primero
    try {
      final healthResponse = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: _defaultHeaders,
      );
      print('Health check status: ${healthResponse.statusCode}');
    } catch (e) {
      print('Error en health check: $e');
    }
    print('============================');
  }

  // Obtener todos los usuarios
  static Future<List<User>> getAllUsers() async {
    try {
      // Debug de autenticación
      await debugAuth();

      final response = await http.get(
        Uri.parse('$baseUrl$usersEndpoint/'),
        headers: await _getAuthHeaders(),
      );

      print('Response status: ${response.statusCode}');
      print('Response body: ${response.body}');

      if (response.statusCode == 200) {
        final dynamic responseData = jsonDecode(response.body);

        // Verificar si la respuesta es una lista
        if (responseData is List) {
          final List<dynamic> usersJson = responseData;
          return usersJson.map((json) => User.fromJson(json)).toList();
        } else if (responseData is Map<String, dynamic>) {
          // Si es un objeto, podría ser un error o un wrapper
          if (responseData.containsKey('detail')) {
            throw Exception('Error del servidor: ${responseData['detail']}');
          } else if (responseData.containsKey('users')) {
            // Si tiene una clave 'users', usar esa
            final List<dynamic> usersJson = responseData['users'];
            return usersJson.map((json) => User.fromJson(json)).toList();
          } else {
            throw Exception('Formato de respuesta inesperado: $responseData');
          }
        } else {
          throw Exception(
            'Tipo de respuesta inesperado: ${responseData.runtimeType}',
          );
        }
      } else if (response.statusCode == 401) {
        throw Exception('No autorizado. Por favor, inicia sesión nuevamente.');
      } else if (response.statusCode == 403) {
        throw Exception('Acceso denegado. Se requiere rol de administrador.');
      } else {
        final dynamic errorData = jsonDecode(response.body);
        final String errorMessage = errorData is Map<String, dynamic>
            ? (errorData['detail'] ?? 'Error desconocido')
            : 'Error al obtener usuarios: ${response.statusCode}';
        throw Exception(errorMessage);
      }
    } catch (e) {
      if (e.toString().contains('Exception:')) {
        rethrow;
      }
      throw Exception('Error de conexión: $e');
    }
  }

  // Obtener usuario por ID
  static Future<User> getUserById(int id) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl$usersEndpoint/$id'),
        headers: await _getAuthHeaders(),
      );

      if (response.statusCode == 200) {
        final userJson = jsonDecode(response.body);
        return User.fromJson(userJson);
      } else {
        throw Exception('Error al obtener usuario: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Crear nuevo usuario
  static Future<User> createUser({
    required String email,
    required String password,
    required String fullName,
    String? phone,
    required int roleId,
  }) async {
    try {
      print('=== CREAR USUARIO ===');
      await debugAuth();

      final response = await http.post(
        Uri.parse('$baseUrl$usersEndpoint/'),
        headers: await _getAuthHeaders(),
        body: jsonEncode({
          'email': email,
          'password': password,
          'full_name': fullName,
          'phone': phone,
          'role_id': roleId,
        }),
      );

      print('Create user response status: ${response.statusCode}');
      print('Create user response body: ${response.body}');

      if (response.statusCode == 201 || response.statusCode == 200) {
        final userJson = jsonDecode(response.body);
        print('Usuario creado exitosamente');
        return User.fromJson(userJson);
      } else {
        if (response.body.isNotEmpty) {
          final errorData = jsonDecode(response.body);
          throw Exception(errorData['detail'] ?? 'Error al crear usuario');
        } else {
          throw Exception('Error al crear usuario: ${response.statusCode}');
        }
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Actualizar usuario
  static Future<User> updateUser({
    required int id,
    String? email,
    String? fullName,
    String? phone,
    int? roleId,
    bool? isActive,
  }) async {
    try {
      final Map<String, dynamic> updateData = {};
      if (email != null) updateData['email'] = email;
      if (fullName != null) updateData['full_name'] = fullName;
      if (phone != null) updateData['phone'] = phone;
      if (roleId != null) updateData['role_id'] = roleId;
      if (isActive != null) updateData['is_active'] = isActive;

      final response = await http.put(
        Uri.parse('$baseUrl$usersEndpoint/$id'),
        headers: await _getAuthHeaders(),
        body: jsonEncode(updateData),
      );

      if (response.statusCode == 200) {
        final userJson = jsonDecode(response.body);
        return User.fromJson(userJson);
      } else {
        if (response.body.isNotEmpty) {
          final errorData = jsonDecode(response.body);
          throw Exception(errorData['detail'] ?? 'Error al actualizar usuario');
        } else {
          throw Exception(
            'Error al actualizar usuario: ${response.statusCode}',
          );
        }
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Eliminar usuario
  static Future<void> deleteUser(int id) async {
    try {
      print('=== ELIMINAR USUARIO ===');
      await debugAuth();

      final response = await http.delete(
        Uri.parse('$baseUrl$usersEndpoint/$id'),
        headers: await _getAuthHeaders(),
      );

      print('Delete user response status: ${response.statusCode}');
      print('Delete user response body: ${response.body}');

      if (response.statusCode == 204 || response.statusCode == 200) {
        // Operación exitosa - código 204 (No Content) o 200 (OK)
        print('Usuario eliminado exitosamente');
        return;
      } else {
        if (response.body.isNotEmpty) {
          final errorData = jsonDecode(response.body);
          throw Exception(errorData['detail'] ?? 'Error al eliminar usuario');
        } else {
          throw Exception('Error al eliminar usuario: ${response.statusCode}');
        }
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // Obtener todos los roles
  static Future<List<Map<String, dynamic>>> getAllRoles() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl$rolesEndpoint/'),
        headers: await _getAuthHeaders(),
      );

      print('Roles response status: ${response.statusCode}');
      print('Roles response body: ${response.body}');

      if (response.statusCode == 200) {
        final dynamic responseData = jsonDecode(response.body);

        if (responseData is List) {
          final List<dynamic> rolesJson = responseData;
          return rolesJson.cast<Map<String, dynamic>>();
        } else if (responseData is Map<String, dynamic>) {
          if (responseData.containsKey('detail')) {
            throw Exception('Error del servidor: ${responseData['detail']}');
          } else if (responseData.containsKey('roles')) {
            final List<dynamic> rolesJson = responseData['roles'];
            return rolesJson.cast<Map<String, dynamic>>();
          } else {
            throw Exception(
              'Formato de respuesta inesperado para roles: $responseData',
            );
          }
        } else {
          throw Exception(
            'Tipo de respuesta inesperado para roles: ${responseData.runtimeType}',
          );
        }
      } else if (response.statusCode == 401) {
        throw Exception('No autorizado. Por favor, inicia sesión nuevamente.');
      } else if (response.statusCode == 403) {
        throw Exception('Acceso denegado. Se requiere rol de administrador.');
      } else {
        final dynamic errorData = jsonDecode(response.body);
        final String errorMessage = errorData is Map<String, dynamic>
            ? (errorData['detail'] ?? 'Error desconocido')
            : 'Error al obtener roles: ${response.statusCode}';
        throw Exception(errorMessage);
      }
    } catch (e) {
      if (e.toString().contains('Exception:')) {
        rethrow;
      }
      throw Exception('Error de conexión: $e');
    }
  }
}
