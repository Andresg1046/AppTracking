import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:math' as math;
import '../../providers/auth_provider.dart';
import '../../providers/theme_provider.dart';
import '../auth/login_screen.dart';

class DriverHomeScreen extends StatefulWidget {
  const DriverHomeScreen({super.key});

  @override
  State<DriverHomeScreen> createState() => _DriverHomeScreenState();
}

class _DriverHomeScreenState extends State<DriverHomeScreen> with SingleTickerProviderStateMixin {
  int _selectedIndex = 0;
  late final PageController _pageController;

  @override
  void initState() {
    super.initState();
    _pageController = PageController(initialPage: _selectedIndex);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
    _pageController.animateToPage(
      index,
      duration: const Duration(milliseconds: 420),
      curve: Curves.easeOutCubic,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        final isDark = themeProvider.isDarkMode;
        
        return Scaffold(
          backgroundColor: themeProvider.getBackgroundColor(isDark),
          body: PageView(
            controller: _pageController,
            onPageChanged: (i) => setState(() => _selectedIndex = i),
            children: [
              _buildDashboardTab(isDark),
              _buildVehicleTab(isDark),
              _buildRouteTab(isDark),
              _buildHistoryTab(isDark),
              _buildProfileTab(isDark),
            ],
          ),
          bottomNavigationBar: Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 20),
            child: ConvexBottomBar(
              currentIndex: _selectedIndex,
              onTap: _onItemTapped,
              isDark: isDark,
              items: const [
                BottomBarItem(icon: Icons.home_rounded, label: 'Inicio'),
                BottomBarItem(icon: Icons.directions_car_rounded, label: 'Mi Vehículo'),
                BottomBarItem(icon: Icons.route_rounded, label: 'Ruta'),
                BottomBarItem(icon: Icons.history_rounded, label: 'Historial'),
                BottomBarItem(icon: Icons.person_rounded, label: 'Perfil'),
              ],
            ),
          ),
        );
      },
    );
  }


  Widget _buildDashboardTab(bool isDark) {
    return Consumer2<AuthProvider, ThemeProvider>(
      builder: (context, authProvider, themeProvider, child) {
        final user = authProvider.user;
        
        return Scaffold(
          backgroundColor: themeProvider.getBackgroundColor(isDark),
          appBar: AppBar(
            title: Text(
              'Panel del Conductor',
              style: TextStyle(color: themeProvider.getTextColor(isDark)),
            ),
            backgroundColor: themeProvider.getBackgroundColor(isDark),
            foregroundColor: themeProvider.getTextColor(isDark),
            elevation: 0,
            actions: [
              IconButton(
                icon: Icon(
                  isDark ? Icons.light_mode : Icons.dark_mode,
                  color: themeProvider.getTextColor(isDark),
                ),
                onPressed: () {
                  themeProvider.toggleTheme();
                },
              ),
              Consumer<AuthProvider>(
                builder: (context, authProvider, child) {
                  return PopupMenuButton<String>(
                    onSelected: (value) async {
                      if (value == 'logout') {
                        await authProvider.logout();
                        if (context.mounted) {
                          Navigator.of(context).pushReplacement(
                            MaterialPageRoute(builder: (context) => const LoginScreen()),
                          );
                        }
                      }
                    },
                    itemBuilder: (context) => [
                      const PopupMenuItem(
                        value: 'logout',
                        child: Row(
                          children: [
                            Icon(Icons.logout),
                            SizedBox(width: 8),
                            Text('Cerrar Sesión'),
                          ],
                        ),
                      ),
                    ],
                  );
                },
              ),
            ],
          ),
          body: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Welcome card
                Container(
                  decoration: BoxDecoration(
                    color: themeProvider.getCardColor(isDark),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isDark 
                          ? Colors.white.withOpacity(0.1) 
                          : Colors.grey.withOpacity(0.2)
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: isDark 
                            ? Colors.black.withOpacity(0.3) 
                            : Colors.grey.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.drive_eta_rounded,
                              color: themeProvider.getPrimaryColor(isDark),
                              size: 32,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    '¡Bienvenido, Conductor!',
                                    style: TextStyle(
                                      fontSize: 20,
                                      fontWeight: FontWeight.bold,
                                      color: themeProvider.getTextColor(isDark),
                                    ),
                                  ),
                                  Text(
                                    'Hola, ${user?.fullName ?? 'Usuario'}',
                                    style: TextStyle(
                                      fontSize: 16,
                                      color: themeProvider.getSecondaryTextColor(isDark),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // Status card
                Container(
                  decoration: BoxDecoration(
                    color: themeProvider.getCardColor(isDark),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isDark 
                          ? Colors.white.withOpacity(0.1) 
                          : Colors.grey.withOpacity(0.2)
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: isDark 
                            ? Colors.black.withOpacity(0.3) 
                            : Colors.grey.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Estado Actual',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: themeProvider.getTextColor(isDark),
                          ),
                        ),
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            Container(
                              width: 12,
                              height: 12,
                              decoration: const BoxDecoration(
                                color: Colors.green,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Disponible',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: themeProvider.getTextColor(isDark),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Listo para recibir asignaciones',
                          style: TextStyle(
                            fontSize: 14,
                            color: themeProvider.getSecondaryTextColor(isDark),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // Quick actions
                Text(
                  'Acciones Rápidas',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: themeProvider.getTextColor(isDark),
                  ),
                ),
                const SizedBox(height: 16),
                
                Expanded(
                  child: GridView.count(
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    children: [
                      _buildActionCard(
                        context,
                        isDark: isDark,
                        icon: Icons.directions_car_rounded,
                        title: 'Mi Vehículo',
                        subtitle: 'Ver detalles',
                        onTap: () {
                          _onItemTapped(1);
                        },
                      ),
                      _buildActionCard(
                        context,
                        isDark: isDark,
                        icon: Icons.route_rounded,
                        title: 'Ruta Actual',
                        subtitle: 'Ver ruta',
                        onTap: () {
                          _onItemTapped(2);
                        },
                      ),
                      _buildActionCard(
                        context,
                        isDark: isDark,
                        icon: Icons.history_rounded,
                        title: 'Historial',
                        subtitle: 'Ver viajes',
                        onTap: () {
                          _onItemTapped(3);
                        },
                      ),
                      _buildActionCard(
                        context,
                        isDark: isDark,
                        icon: Icons.person_rounded,
                        title: 'Perfil',
                        subtitle: 'Ver perfil',
                        onTap: () {
                          _onItemTapped(4);
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildVehicleTab(bool isDark) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return Scaffold(
          backgroundColor: themeProvider.getBackgroundColor(isDark),
          appBar: AppBar(
            title: Text(
              'Mi Vehículo',
              style: TextStyle(color: themeProvider.getTextColor(isDark)),
            ),
            backgroundColor: themeProvider.getBackgroundColor(isDark),
            foregroundColor: themeProvider.getTextColor(isDark),
            elevation: 0,
          ),
          body: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                // Vehicle info card
                Container(
                  decoration: BoxDecoration(
                    color: themeProvider.getCardColor(isDark),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isDark 
                          ? Colors.white.withOpacity(0.1) 
                          : Colors.grey.withOpacity(0.2)
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: isDark 
                            ? Colors.black.withOpacity(0.3) 
                            : Colors.grey.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.directions_car_rounded,
                              color: themeProvider.getPrimaryColor(isDark),
                              size: 32,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Vehículo Asignado',
                                    style: TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: themeProvider.getTextColor(isDark),
                                    ),
                                  ),
                                  Text(
                                    'ABC-123',
                                    style: TextStyle(
                                      fontSize: 16,
                                      color: themeProvider.getSecondaryTextColor(isDark),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            Expanded(
                              child: _buildVehicleInfo(
                                'Marca',
                                'Toyota',
                                isDark,
                                themeProvider,
                              ),
                            ),
                            Expanded(
                              child: _buildVehicleInfo(
                                'Modelo',
                                'Corolla',
                                isDark,
                                themeProvider,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: _buildVehicleInfo(
                                'Año',
                                '2022',
                                isDark,
                                themeProvider,
                              ),
                            ),
                            Expanded(
                              child: _buildVehicleInfo(
                                'Estado',
                                'Activo',
                                isDark,
                                themeProvider,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // Vehicle actions
                Expanded(
                  child: ListView(
                    children: [
                      _buildVehicleAction(
                        context,
                        isDark: isDark,
                        icon: Icons.info_rounded,
                        title: 'Información Detallada',
                        subtitle: 'Ver especificaciones completas',
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Funcionalidad en desarrollo')),
                          );
                        },
                      ),
                      _buildVehicleAction(
                        context,
                        isDark: isDark,
                        icon: Icons.build_rounded,
                        title: 'Mantenimiento',
                        subtitle: 'Historial de mantenimientos',
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Funcionalidad en desarrollo')),
                          );
                        },
                      ),
                      _buildVehicleAction(
                        context,
                        isDark: isDark,
                        icon: Icons.local_gas_station_rounded,
                        title: 'Combustible',
                        subtitle: 'Registrar consumo',
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Funcionalidad en desarrollo')),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildRouteTab(bool isDark) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return Scaffold(
          backgroundColor: themeProvider.getBackgroundColor(isDark),
          appBar: AppBar(
            title: Text(
              'Ruta Actual',
              style: TextStyle(color: themeProvider.getTextColor(isDark)),
            ),
            backgroundColor: themeProvider.getBackgroundColor(isDark),
            foregroundColor: themeProvider.getTextColor(isDark),
            elevation: 0,
          ),
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.route_rounded, 
                  size: 64, 
                  color: themeProvider.getSecondaryTextColor(isDark)
                ),
                const SizedBox(height: 16),
                Text(
                  'Ruta Actual',
                  style: TextStyle(
                    fontSize: 24, 
                    fontWeight: FontWeight.bold, 
                    color: themeProvider.getTextColor(isDark)
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'No hay ruta asignada',
                  style: TextStyle(color: themeProvider.getSecondaryTextColor(isDark)),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildHistoryTab(bool isDark) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return Scaffold(
          backgroundColor: themeProvider.getBackgroundColor(isDark),
          appBar: AppBar(
            title: Text(
              'Historial de Viajes',
              style: TextStyle(color: themeProvider.getTextColor(isDark)),
            ),
            backgroundColor: themeProvider.getBackgroundColor(isDark),
            foregroundColor: themeProvider.getTextColor(isDark),
            elevation: 0,
          ),
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.history_rounded, 
                  size: 64, 
                  color: themeProvider.getSecondaryTextColor(isDark)
                ),
                const SizedBox(height: 16),
                Text(
                  'Historial de Viajes',
                  style: TextStyle(
                    fontSize: 24, 
                    fontWeight: FontWeight.bold, 
                    color: themeProvider.getTextColor(isDark)
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Funcionalidad en desarrollo',
                  style: TextStyle(color: themeProvider.getSecondaryTextColor(isDark)),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildProfileTab(bool isDark) {
    return Consumer2<AuthProvider, ThemeProvider>(
      builder: (context, authProvider, themeProvider, child) {
        final user = authProvider.user;
        
        return Scaffold(
          backgroundColor: themeProvider.getBackgroundColor(isDark),
          appBar: AppBar(
            title: Text(
              'Perfil del Conductor',
              style: TextStyle(color: themeProvider.getTextColor(isDark)),
            ),
            backgroundColor: themeProvider.getBackgroundColor(isDark),
            foregroundColor: themeProvider.getTextColor(isDark),
            elevation: 0,
          ),
          body: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                // Profile header
                Container(
                  decoration: BoxDecoration(
                    color: themeProvider.getCardColor(isDark),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isDark 
                          ? Colors.white.withOpacity(0.1) 
                          : Colors.grey.withOpacity(0.2)
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: isDark 
                            ? Colors.black.withOpacity(0.3) 
                            : Colors.grey.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      children: [
                        CircleAvatar(
                          radius: 50,
                          backgroundColor: themeProvider.getPrimaryColor(isDark),
                          child: Icon(
                            Icons.drive_eta_rounded,
                            size: 40,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          user?.fullName ?? 'Conductor',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: themeProvider.getTextColor(isDark),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          user?.email ?? '',
                          style: TextStyle(
                            color: themeProvider.getSecondaryTextColor(isDark),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: themeProvider.getPrimaryColor(isDark),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            'Conductor',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // Driver options
                Expanded(
                  child: ListView(
                    children: [
                      _buildProfileOption(
                        context,
                        isDark: isDark,
                        icon: Icons.edit_rounded,
                        title: 'Editar Perfil',
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Funcionalidad en desarrollo')),
                          );
                        },
                      ),
                      _buildProfileOption(
                        context,
                        isDark: isDark,
                        icon: Icons.card_membership_rounded,
                        title: 'Licencia de Conducir',
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Funcionalidad en desarrollo')),
                          );
                        },
                      ),
                      _buildProfileOption(
                        context,
                        isDark: isDark,
                        icon: Icons.help_rounded,
                        title: 'Ayuda',
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Funcionalidad en desarrollo')),
                          );
                        },
                      ),
                      _buildProfileOption(
                        context,
                        isDark: isDark,
                        icon: Icons.logout_rounded,
                        title: 'Cerrar Sesión',
                        onTap: () async {
                          await authProvider.logout();
                          if (context.mounted) {
                            Navigator.of(context).pushReplacement(
                              MaterialPageRoute(builder: (context) => const LoginScreen()),
                            );
                          }
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildVehicleInfo(String label, String value, bool isDark, ThemeProvider themeProvider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: themeProvider.getSecondaryTextColor(isDark),
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: themeProvider.getTextColor(isDark),
          ),
        ),
      ],
    );
  }

  Widget _buildActionCard(
    BuildContext context, {
    required bool isDark,
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return Container(
          decoration: BoxDecoration(
            color: themeProvider.getCardColor(isDark),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: isDark 
                  ? Colors.white.withOpacity(0.1) 
                  : Colors.grey.withOpacity(0.2)
            ),
            boxShadow: [
              BoxShadow(
                color: isDark 
                    ? Colors.black.withOpacity(0.2) 
                    : Colors.grey.withOpacity(0.1),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(16),
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    icon,
                    size: 48,
                    color: themeProvider.getSecondaryTextColor(isDark),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: themeProvider.getTextColor(isDark),
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 12,
                      color: themeProvider.getSecondaryTextColor(isDark),
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildVehicleAction(
    BuildContext context, {
    required bool isDark,
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return Container(
          margin: const EdgeInsets.only(bottom: 8),
          decoration: BoxDecoration(
            color: themeProvider.getCardColor(isDark),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isDark 
                  ? Colors.white.withOpacity(0.1) 
                  : Colors.grey.withOpacity(0.2)
            ),
            boxShadow: [
              BoxShadow(
                color: isDark 
                    ? Colors.black.withOpacity(0.2) 
                    : Colors.grey.withOpacity(0.1),
                blurRadius: 4,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: ListTile(
            leading: Icon(icon, color: themeProvider.getSecondaryTextColor(isDark)),
            title: Text(
              title,
              style: TextStyle(color: themeProvider.getTextColor(isDark)),
            ),
            subtitle: Text(
              subtitle,
              style: TextStyle(color: themeProvider.getSecondaryTextColor(isDark)),
            ),
            trailing: Icon(
              Icons.arrow_forward_ios, 
              size: 16, 
              color: themeProvider.getSecondaryTextColor(isDark)
            ),
            onTap: onTap,
          ),
        );
      },
    );
  }

  Widget _buildProfileOption(
    BuildContext context, {
    required bool isDark,
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return Container(
          margin: const EdgeInsets.only(bottom: 8),
          decoration: BoxDecoration(
            color: themeProvider.getCardColor(isDark),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isDark 
                  ? Colors.white.withOpacity(0.1) 
                  : Colors.grey.withOpacity(0.2)
            ),
            boxShadow: [
              BoxShadow(
                color: isDark 
                    ? Colors.black.withOpacity(0.2) 
                    : Colors.grey.withOpacity(0.1),
                blurRadius: 4,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: ListTile(
            leading: Icon(icon, color: themeProvider.getSecondaryTextColor(isDark)),
            title: Text(
              title,
              style: TextStyle(color: themeProvider.getTextColor(isDark)),
            ),
            trailing: Icon(
              Icons.arrow_forward_ios, 
              size: 16, 
              color: themeProvider.getSecondaryTextColor(isDark)
            ),
            onTap: onTap,
          ),
        );
      },
    );
  }
}

class BottomBarItem {
  final IconData icon;
  final String label;
  const BottomBarItem({required this.icon, required this.label});
}

/// A convex-style animated bottom bar with a rising bump and circular chip on the active icon.
class ConvexBottomBar extends StatefulWidget {
  final List<BottomBarItem> items;
  final int currentIndex;
  final ValueChanged<int> onTap;
  final bool isDark;
  final double height;
  final double radius;
  final double bumpWidth; // span horizontal del bump
  final double bumpHeight; // altura del bump
  final double edgePadding; // margen seguro respecto a esquinas redondeadas
  final double sideInset; // separación interna izquierda/derecha para que los tabs extremos no peguen a las esquinas

  const ConvexBottomBar({
    super.key,
    required this.items,
    required this.currentIndex,
    required this.onTap,
    required this.isDark,
    this.height = 72,
    this.radius = 26,
    this.bumpWidth = 92,
    this.bumpHeight = 24,
    this.edgePadding = 12,
    this.sideInset = 28,
  }) : assert(items.length >= 2 && items.length <= 5, 'Use 2–5 items for best layout');

  @override
  State<ConvexBottomBar> createState() => _ConvexBottomBarState();
}

class _ConvexBottomBarState extends State<ConvexBottomBar> {
  double _centerX = 0;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final barWidth = constraints.maxWidth;
        final itemCount = widget.items.length;

        // 1) calculamos ancho útil descontando un sideInset (que puede aumentar dinámicamente)
        double effectiveInset = widget.sideInset;
        double contentWidth = barWidth - 2 * effectiveInset;
        double itemWidth = contentWidth / itemCount;

        // 2) si el primer/último tab no tienen espacio para el bump completo, aumentamos el inset automáticamente
        final minInsetForFullBump = widget.radius + widget.edgePadding + widget.bumpWidth / 2 - itemWidth / 2 + 1;
        if (minInsetForFullBump > effectiveInset) {
          effectiveInset = minInsetForFullBump;
          contentWidth = barWidth - 2 * effectiveInset;
          itemWidth = contentWidth / itemCount;
        }

        final targetX = effectiveInset + (widget.currentIndex + 0.5) * itemWidth;

        return TweenAnimationBuilder<double>(
          duration: const Duration(milliseconds: 420),
          curve: Curves.easeOutCubic,
          tween: Tween<double>(begin: _centerX == 0 ? targetX : _centerX, end: targetX),
          onEnd: () => _centerX = targetX,
          builder: (context, cx, child) {
            final circleSize = 44.0;
            final clipper = _ConvexClipper(
              radius: widget.radius,
              bumpWidth: widget.bumpWidth,
              bumpHeight: widget.bumpHeight,
              edgePadding: widget.edgePadding,
              centerX: cx,
            );

            return SizedBox(
              height: widget.height,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Fondo pintado + chip, ambos recortados a la misma silueta para evitar desbordes
                  ClipPath(
                    clipper: clipper,
                    child: Stack(
                      children: [
                        Consumer<ThemeProvider>(
                          builder: (context, themeProvider, child) {
                            return CustomPaint(
                              size: Size(barWidth, widget.height),
                              painter: _ConvexPainter(
                                radius: widget.radius,
                                bumpWidth: widget.bumpWidth,
                                bumpHeight: widget.bumpHeight,
                                edgePadding: widget.edgePadding,
                                centerX: cx,
                                background: themeProvider.getSurfaceColor(widget.isDark),
                                shadow: widget.isDark ? Colors.black54 : Colors.grey.withOpacity(0.3),
                              ),
                            );
                          },
                        ),
                        Positioned(
                          top: 4,
                          left: cx - circleSize / 2,
                          child: Consumer<ThemeProvider>(
                            builder: (context, themeProvider, child) {
                              return Container(
                                width: circleSize,
                                height: circleSize,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: themeProvider.getPrimaryColor(widget.isDark),
                                ),
                              );
                            },
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Íconos alineados al mismo contentWidth (con padding lateral) para que coincidan con el bump
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: effectiveInset),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        for (var i = 0; i < itemCount; i++)
                          _NavItem(
                            item: widget.items[i],
                            active: i == widget.currentIndex,
                            isDark: widget.isDark,
                            onTap: () => widget.onTap(i),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}

class _ConvexPainter extends CustomPainter {
  final double radius;
  final double bumpWidth;
  final double bumpHeight;
  final double edgePadding;
  final double centerX;
  final Color background;
  final Color shadow;

  _ConvexPainter({
    required this.radius,
    required this.bumpWidth,
    required this.bumpHeight,
    required this.edgePadding,
    required this.centerX,
    required this.background,
    required this.shadow,
  });

  Path _buildPath(Size size) {
    final path = Path();
    final left = 0.0;
    final right = size.width;
    final top = 0.0;
    final bottom = size.height;

    final leftLimit = radius + edgePadding;
    final rightLimit = size.width - radius - edgePadding;

    final halfIdeal = bumpWidth / 2;
    double half = math.min(halfIdeal, centerX - leftLimit);
    half = math.min(half, rightLimit - centerX);
    half = half.clamp(18.0, halfIdeal); // mínimo más grande para que no se vea diminuto

    final start = centerX - half;
    final end = centerX + half;

    final widthScale = (half / halfIdeal).clamp(0.85, 1.0); // altura casi constante cerca de bordes
    final height = bumpHeight * widthScale;

    path.moveTo(left + radius, top);
    path.lineTo(start, top);

    final cp1 = Offset(start + half * 0.35, top);
    final cp2 = Offset(centerX - half * 0.35, -height);
    final apex = Offset(centerX, -height);
    path.cubicTo(cp1.dx, cp1.dy, cp2.dx, cp2.dy, apex.dx, apex.dy);

    final cp3 = Offset(centerX + half * 0.35, -height);
    final cp4 = Offset(end - half * 0.35, top);
    path.cubicTo(cp3.dx, cp3.dy, cp4.dx, cp4.dy, end, top);

    path.lineTo(right - radius, top);
    path.arcToPoint(Offset(right, top + radius), radius: Radius.circular(radius));
    path.lineTo(right, bottom - radius);
    path.arcToPoint(Offset(right - radius, bottom), radius: Radius.circular(radius));
    path.lineTo(left + radius, bottom);
    path.arcToPoint(Offset(left, bottom - radius), radius: Radius.circular(radius));
    path.lineTo(left, top + radius);
    path.arcToPoint(Offset(left + radius, top), radius: Radius.circular(radius));

    return path;
  }

  @override
  void paint(Canvas canvas, Size size) {
    final path = _buildPath(size);

    final shadowPaint = Paint()
      ..color = shadow.withOpacity(0.35)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 12);
    canvas.drawPath(path.shift(const Offset(0, 6)), shadowPaint);

    final paint = Paint()..color = background;
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _ConvexPainter old) {
    return old.centerX != centerX ||
        old.bumpWidth != bumpWidth ||
        old.bumpHeight != bumpHeight ||
        old.edgePadding != edgePadding ||
        old.background != background ||
        old.radius != radius;
  }
}

class _ConvexClipper extends CustomClipper<Path> {
  final double radius;
  final double bumpWidth;
  final double bumpHeight;
  final double edgePadding;
  final double centerX;

  _ConvexClipper({
    required this.radius,
    required this.bumpWidth,
    required this.bumpHeight,
    required this.edgePadding,
    required this.centerX,
  });

  @override
  Path getClip(Size size) {
    final painter = _ConvexPainter(
      radius: radius,
      bumpWidth: bumpWidth,
      bumpHeight: bumpHeight,
      edgePadding: edgePadding,
      centerX: centerX,
      background: Colors.transparent,
      shadow: Colors.transparent,
    );
    return painter._buildPath(size);
  }

  @override
  bool shouldReclip(covariant _ConvexClipper old) {
    return old.centerX != centerX ||
        old.bumpWidth != bumpWidth ||
        old.bumpHeight != bumpHeight ||
        old.edgePadding != edgePadding ||
        old.radius != radius;
  }
}

class _NavItem extends StatefulWidget {
  final BottomBarItem item;
  final bool active;
  final bool isDark;
  final VoidCallback onTap;
  const _NavItem({required this.item, required this.active, required this.isDark, required this.onTap});

  @override
  State<_NavItem> createState() => _NavItemState();
}

class _NavItemState extends State<_NavItem> {
  @override
  Widget build(BuildContext context) {
    final active = widget.active;
    return Expanded(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 220),
          curve: Curves.easeOut,
          padding: const EdgeInsets.symmetric(horizontal: 8),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              AnimatedScale(
                duration: const Duration(milliseconds: 260),
                curve: Curves.elasticOut,
                scale: active ? 1.15 : 1.0,
                child: Consumer<ThemeProvider>(
                  builder: (context, themeProvider, child) {
                    return Icon(
                      widget.item.icon,
                      size: 26,
                      color: active 
                          ? Colors.white 
                          : themeProvider.getSecondaryTextColor(widget.isDark),
                    );
                  },
                ),
              ),
              const SizedBox(height: 6),
              AnimatedOpacity(
                duration: const Duration(milliseconds: 200),
                opacity: active ? 1 : 0,
                child: Consumer<ThemeProvider>(
                  builder: (context, themeProvider, child) {
                    return Text(
                      widget.item.label,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 12, 
                        fontWeight: FontWeight.w600, 
                        color: Colors.white
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
