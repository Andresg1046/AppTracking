import 'package:flutter/material.dart';

class ResponsiveAuthContainer extends StatelessWidget {
  final Widget child;
  final double? maxWidth;

  const ResponsiveAuthContainer({
    super.key,
    required this.child,
    this.maxWidth,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    
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

    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          physics: const ClampingScrollPhysics(),
          child: ConstrainedBox(
            constraints: BoxConstraints(
              minHeight: constraints.maxHeight,
            ),
            child: IntrinsicHeight(
              child: Center(
                child: Container(
                  width: maxWidth ?? calculatedMaxWidth,
                  padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
                  child: child,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
