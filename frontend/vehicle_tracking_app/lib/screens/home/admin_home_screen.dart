import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:math' as math;
import '../../providers/auth_provider.dart';
import '../../providers/theme_provider.dart';
import '../auth/login_screen.dart';
import '../users/user_management_screen.dart';

class AdminHomeScreen extends StatefulWidget {
  const AdminHomeScreen({super.key});

  @override
  State<AdminHomeScreen> createState() => _AdminHomeScreenState();
}

class _AdminHomeScreenState extends State<AdminHomeScreen> with SingleTickerProviderStateMixin {
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
              _buildVehiclesTab(isDark),
              _buildDriversTab(isDark),
              _buildReportsTab(isDark),
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
                BottomBarItem(icon: Icons.dashboard_rounded, label: 'Dashboard'),
                BottomBarItem(icon: Icons.directions_car_rounded, label: 'Vehículos'),
                BottomBarItem(icon: Icons.person_rounded, label: 'Conductores'),
                BottomBarItem(icon: Icons.analytics_rounded, label: 'Reportes'),
                BottomBarItem(icon: Icons.settings_rounded, label: 'Perfil'),
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
              'Panel de Administración',
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
                              Icons.admin_panel_settings_rounded,
                              color: themeProvider.getPrimaryColor(isDark),
                              size: 32,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    '¡Bienvenido, Administrador!',
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
                
                // Admin stats
                Text(
                  'Estadísticas Generales',
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
                      _buildStatCard(
                        context,
                        isDark: isDark,
                        icon: Icons.directions_car_rounded,
                        title: 'Vehículos',
                        value: '12',
                        subtitle: 'Activos',
                        color: Colors.blue,
                      ),
                      _buildStatCard(
                        context,
                        isDark: isDark,
                        icon: Icons.person_rounded,
                        title: 'Conductores',
                        value: '8',
                        subtitle: 'Registrados',
                        color: Colors.green,
                      ),
                      _buildStatCard(
                        context,
                        isDark: isDark,
                        icon: Icons.route_rounded,
                        title: 'Rutas',
                        value: '25',
                        subtitle: 'En curso',
                        color: Colors.orange,
                      ),
                      _buildStatCard(
                        context,
                        isDark: isDark,
                        icon: Icons.analytics_rounded,
                        title: 'Reportes',
                        value: '156',
                        subtitle: 'Este mes',
                        color: Colors.purple,
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

  Widget _buildVehiclesTab(bool isDark) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return Scaffold(
          backgroundColor: themeProvider.getBackgroundColor(isDark),
          appBar: AppBar(
            title: Text(
              'Gestión de Vehículos',
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
                  Icons.directions_car_rounded, 
                  size: 64, 
                  color: themeProvider.getSecondaryTextColor(isDark)
                ),
                const SizedBox(height: 16),
                Text(
                  'Gestión de Vehículos',
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

  Widget _buildDriversTab(bool isDark) {
    return const UserManagementScreen();
  }

  Widget _buildReportsTab(bool isDark) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return Scaffold(
          backgroundColor: themeProvider.getBackgroundColor(isDark),
          appBar: AppBar(
            title: Text(
              'Reportes y Análisis',
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
                  Icons.analytics_rounded, 
                  size: 64, 
                  color: themeProvider.getSecondaryTextColor(isDark)
                ),
                const SizedBox(height: 16),
                Text(
                  'Reportes y Análisis',
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
              'Perfil de Administrador',
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
                            Icons.admin_panel_settings_rounded,
                            size: 40,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          user?.fullName ?? 'Administrador',
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
                            'Administrador',
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
                
                // Admin options
                Expanded(
                  child: ListView(
                    children: [
                      _buildProfileOption(
                        context,
                        isDark: isDark,
                        icon: Icons.settings_rounded,
                        title: 'Configuración del Sistema',
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Funcionalidad en desarrollo')),
                          );
                        },
                      ),
                      _buildProfileOption(
                        context,
                        isDark: isDark,
                        icon: Icons.security_rounded,
                        title: 'Seguridad y Permisos',
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Funcionalidad en desarrollo')),
                          );
                        },
                      ),
                      _buildProfileOption(
                        context,
                        isDark: isDark,
                        icon: Icons.backup_rounded,
                        title: 'Respaldo de Datos',
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

  Widget _buildStatCard(
    BuildContext context, {
    required bool isDark,
    required IconData icon,
    required String title,
    required String value,
    required String subtitle,
    required Color color,
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
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  icon,
                  size: 32,
                  color: color,
                ),
                const SizedBox(height: 8),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: themeProvider.getTextColor(isDark),
                  ),
                ),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: themeProvider.getTextColor(isDark),
                  ),
                ),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 12,
                    color: themeProvider.getSecondaryTextColor(isDark),
                  ),
                ),
              ],
            ),
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
