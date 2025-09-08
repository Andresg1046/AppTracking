import 'package:flutter/material.dart';

class CenteredContainer extends StatelessWidget {
  final Widget child;
  final double? maxWidth;
  final EdgeInsetsGeometry? padding;

  const CenteredContainer({
    super.key,
    required this.child,
    this.maxWidth,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    final safeAreaTop = MediaQuery.of(context).padding.top;
    final safeAreaBottom = MediaQuery.of(context).padding.bottom;
    
    // Calcular el ancho máximo basado en el tamaño de la pantalla
    double calculatedMaxWidth;
    if (screenWidth < 600) {
      // Móvil: usar casi todo el ancho
      calculatedMaxWidth = screenWidth - 48;
    } else if (screenWidth < 1200) {
      // Tablet: ancho fijo
      calculatedMaxWidth = 500;
    } else {
      // Desktop: ancho fijo más pequeño
      calculatedMaxWidth = 400;
    }

    return SizedBox(
      width: screenWidth,
      height: screenHeight,
      child: Center(
        child: SingleChildScrollView(
          physics: const ClampingScrollPhysics(),
          padding: padding ?? const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxWidth: maxWidth ?? calculatedMaxWidth,
              minHeight: screenHeight - safeAreaTop - safeAreaBottom - 32,
            ),
            child: child,
          ),
        ),
      ),
    );
  }
}
