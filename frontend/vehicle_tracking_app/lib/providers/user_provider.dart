import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../models/role.dart';
import '../services/user_service.dart';

class UserProvider with ChangeNotifier {
  List<User> _users = [];
  List<Role> _roles = [];
  bool _isLoading = false;
  String? _error;

  List<User> get users => _users;
  List<Role> get roles => _roles;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Obtener usuarios por rol
  List<User> getUsersByRole(String roleName) {
    return _users.where((user) => user.roleName?.toLowerCase() == roleName.toLowerCase()).toList();
  }

  // Obtener conductores
  List<User> get drivers => getUsersByRole('driver');

  // Obtener administradores
  List<User> get administrators => getUsersByRole('admin');

  // Obtener usuarios regulares
  List<User> get regularUsers => getUsersByRole('user');

  // Cargar todos los usuarios
  Future<void> loadUsers() async {
    _setLoading(true);
    _clearError();
    
    try {
      _users = await UserService.getAllUsers();
      print('Total usuarios cargados: ${_users.length}');
      for (var user in _users) {
        print('Usuario: ${user.fullName}, Rol: ${user.roleName}');
      }
      print('Conductores encontrados: ${drivers.length}');
      print('Administradores encontrados: ${administrators.length}');
      print('Usuarios regulares encontrados: ${regularUsers.length}');
      notifyListeners();
    } catch (e) {
      _setError('Error al cargar usuarios: $e');
    } finally {
      _setLoading(false);
    }
  }

  // Cargar todos los roles
  Future<void> loadRoles() async {
    try {
      final rolesData = await UserService.getAllRoles();
      _roles = rolesData.map((json) => Role.fromJson(json)).toList();
      notifyListeners();
    } catch (e) {
      _setError('Error al cargar roles: $e');
    }
  }

  // Crear nuevo usuario
  Future<bool> createUser({
    required String email,
    required String password,
    required String fullName,
    String? phone,
    required int roleId,
  }) async {
    _setLoading(true);
    _clearError();
    
    try {
      final newUser = await UserService.createUser(
        email: email,
        password: password,
        fullName: fullName,
        phone: phone,
        roleId: roleId,
      );
      
      _users.add(newUser);
      notifyListeners();
      print('Usuario creado exitosamente en el provider');
      return true;
    } catch (e) {
      print('Error en createUser provider: $e');
      _setError('Error al crear usuario: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Actualizar usuario
  Future<bool> updateUser({
    required int id,
    String? email,
    String? fullName,
    String? phone,
    int? roleId,
    bool? isActive,
  }) async {
    _setLoading(true);
    _clearError();
    
    try {
      final updatedUser = await UserService.updateUser(
        id: id,
        email: email,
        fullName: fullName,
        phone: phone,
        roleId: roleId,
        isActive: isActive,
      );
      
      final index = _users.indexWhere((user) => user.id == id);
      if (index != -1) {
        _users[index] = updatedUser;
        notifyListeners();
      }
      return true;
    } catch (e) {
      _setError('Error al actualizar usuario: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Eliminar usuario
  Future<bool> deleteUser(int id) async {
    _setLoading(true);
    _clearError();
    
    try {
      await UserService.deleteUser(id);
      _users.removeWhere((user) => user.id == id);
      notifyListeners();
      print('Usuario eliminado exitosamente del provider');
      return true;
    } catch (e) {
      print('Error en deleteUser provider: $e');
      _setError('Error al eliminar usuario: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Obtener usuario por ID
  User? getUserById(int id) {
    try {
      return _users.firstWhere((user) => user.id == id);
    } catch (e) {
      return null;
    }
  }

  // Obtener rol por ID
  Role? getRoleById(int id) {
    try {
      return _roles.firstWhere((role) => role.id == id);
    } catch (e) {
      return null;
    }
  }

  // Métodos privados
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
  }

  // Limpiar datos
  void clear() {
    _users.clear();
    _roles.clear();
    _error = null;
    _isLoading = false;
    notifyListeners();
  }
}
