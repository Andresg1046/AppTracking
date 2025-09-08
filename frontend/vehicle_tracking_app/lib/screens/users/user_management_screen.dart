import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/user_provider.dart';
import '../../models/user.dart';
import 'create_user_screen.dart';
import 'edit_user_screen.dart';

class UserManagementScreen extends StatefulWidget {
  const UserManagementScreen({super.key});

  @override
  State<UserManagementScreen> createState() => _UserManagementScreenState();
}

class _UserManagementScreenState extends State<UserManagementScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    
    // Cargar datos al inicializar
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final userProvider = Provider.of<UserProvider>(context, listen: false);
      userProvider.loadUsers();
      userProvider.loadRoles();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        final isDark = themeProvider.isDarkMode;
        
        return Scaffold(
          backgroundColor: themeProvider.getBackgroundColor(isDark),
          appBar: AppBar(
            title: Text(
              'Gestión de Usuarios',
              style: TextStyle(color: themeProvider.getTextColor(isDark)),
            ),
            backgroundColor: themeProvider.getBackgroundColor(isDark),
            foregroundColor: themeProvider.getTextColor(isDark),
            elevation: 0,
            bottom: TabBar(
              controller: _tabController,
              indicatorColor: themeProvider.getPrimaryColor(isDark),
              labelColor: themeProvider.getTextColor(isDark),
              unselectedLabelColor: themeProvider.getSecondaryTextColor(isDark),
              tabs: const [
                Tab(
                  icon: Icon(Icons.drive_eta),
                  text: 'Conductores',
                ),
                Tab(
                  icon: Icon(Icons.admin_panel_settings),
                  text: 'Administradores',
                ),
                Tab(
                  icon: Icon(Icons.person),
                  text: 'Usuarios',
                ),
              ],
            ),
          ),
          body: TabBarView(
            controller: _tabController,
            children: [
              _buildUsersTab('driver', isDark, themeProvider),
              _buildUsersTab('admin', isDark, themeProvider),
              _buildUsersTab('user', isDark, themeProvider),
            ],
          ),
          floatingActionButton: FloatingActionButton(
            onPressed: () => _navigateToCreateUser(),
            backgroundColor: themeProvider.getPrimaryColor(isDark),
            child: const Icon(Icons.add, color: Colors.white),
          ),
        );
      },
    );
  }

  Widget _buildUsersTab(String roleName, bool isDark, ThemeProvider themeProvider) {
    return Consumer<UserProvider>(
      builder: (context, userProvider, child) {
        if (userProvider.isLoading) {
          return Center(
            child: CircularProgressIndicator(
              color: themeProvider.getPrimaryColor(isDark),
            ),
          );
        }

        if (userProvider.error != null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.error_outline,
                  size: 64,
                  color: themeProvider.getSecondaryTextColor(isDark),
                ),
                const SizedBox(height: 16),
                Text(
                  'Error al cargar usuarios',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: themeProvider.getTextColor(isDark),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  userProvider.error!,
                  style: TextStyle(color: themeProvider.getSecondaryTextColor(isDark)),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => userProvider.loadUsers(),
                  child: const Text('Reintentar'),
                ),
              ],
            ),
          );
        }

        List<User> users = [];
        switch (roleName) {
          case 'driver':
            users = userProvider.drivers;
            break;
          case 'admin':
            users = userProvider.administrators;
            break;
          case 'user':
            users = userProvider.regularUsers;
            break;
        }

        if (users.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  _getRoleIcon(roleName),
                  size: 64,
                  color: themeProvider.getSecondaryTextColor(isDark),
                ),
                const SizedBox(height: 16),
                Text(
                  'No hay ${_getRoleDisplayName(roleName).toLowerCase()}',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: themeProvider.getTextColor(isDark),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Toca el botón + para crear uno nuevo',
                  style: TextStyle(color: themeProvider.getSecondaryTextColor(isDark)),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: () => userProvider.loadUsers(),
          color: themeProvider.getPrimaryColor(isDark),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: users.length,
            itemBuilder: (context, index) {
              final user = users[index];
              return _buildUserCard(user, isDark, themeProvider);
            },
          ),
        );
      },
    );
  }

  Widget _buildUserCard(User user, bool isDark, ThemeProvider themeProvider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      color: themeProvider.getCardColor(isDark),
      elevation: 2,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: themeProvider.getPrimaryColor(isDark),
          child: Icon(
            Icons.person,
            color: Colors.white,
          ),
        ),
        title: Text(
          user.fullName,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: themeProvider.getTextColor(isDark),
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Teléfono: ${user.phone ?? 'No especificado'}',
              style: TextStyle(color: themeProvider.getSecondaryTextColor(isDark)),
            ),
            Text(
              'Rol: ${user.roleName ?? 'Sin rol'}',
              style: TextStyle(color: themeProvider.getSecondaryTextColor(isDark)),
            ),
            Text(
              'Estado: ${user.isActive ? 'Activo' : 'Inactivo'}',
              style: TextStyle(
                color: user.isActive ? Colors.green : Colors.red,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: Icon(
                Icons.edit,
                color: themeProvider.getPrimaryColor(isDark),
              ),
              onPressed: () => _navigateToEditUser(user),
            ),
            IconButton(
              icon: Icon(
                Icons.delete,
                color: Colors.red,
              ),
              onPressed: () => _showDeleteConfirmation(user),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getRoleIcon(String roleName) {
    switch (roleName) {
      case 'driver':
        return Icons.drive_eta;
      case 'admin':
        return Icons.admin_panel_settings;
      case 'user':
        return Icons.person;
      default:
        return Icons.person;
    }
  }

  String _getRoleDisplayName(String roleName) {
    switch (roleName) {
      case 'driver':
        return 'Conductores';
      case 'admin':
        return 'Administradores';
      case 'user':
        return 'Usuarios';
      default:
        return 'Usuarios';
    }
  }

  void _navigateToCreateUser() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const CreateUserScreen(),
      ),
    );

    if (result == true) {
      // Recargar usuarios si se creó uno nuevo
      final userProvider = Provider.of<UserProvider>(context, listen: false);
      userProvider.loadUsers();
    }
  }

  void _navigateToEditUser(User user) async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EditUserScreen(user: user),
      ),
    );

    if (result == true) {
      // Recargar usuarios si se editó uno
      final userProvider = Provider.of<UserProvider>(context, listen: false);
      userProvider.loadUsers();
    }
  }

  void _showDeleteConfirmation(User user) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Confirmar eliminación'),
        content: Text('¿Estás seguro de que quieres eliminar a ${user.fullName}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _deleteUser(user);
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );
  }

  void _deleteUser(User user) async {
    final userProvider = Provider.of<UserProvider>(context, listen: false);
    final success = await userProvider.deleteUser(user.id);
    
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Usuario ${user.fullName} eliminado correctamente'),
          backgroundColor: Colors.green,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al eliminar usuario: ${userProvider.error}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}
