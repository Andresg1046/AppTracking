import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/user_provider.dart';

class CreateUserScreen extends StatefulWidget {
  const CreateUserScreen({super.key});

  @override
  State<CreateUserScreen> createState() => _CreateUserScreenState();
}

class _CreateUserScreenState extends State<CreateUserScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _fullNameController = TextEditingController();
  final _phoneController = TextEditingController();
  
  int? _selectedRoleId;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // Cargar roles al inicializar
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final userProvider = Provider.of<UserProvider>(context, listen: false);
      userProvider.loadRoles();
    });
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _fullNameController.dispose();
    _phoneController.dispose();
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
              'Crear Usuario',
              style: TextStyle(color: themeProvider.getTextColor(isDark)),
            ),
            backgroundColor: themeProvider.getBackgroundColor(isDark),
            foregroundColor: themeProvider.getTextColor(isDark),
            elevation: 0,
          ),
          body: _isLoading
              ? Center(
                  child: CircularProgressIndicator(
                    color: themeProvider.getPrimaryColor(isDark),
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _buildTextField(
                          controller: _emailController,
                          label: 'Correo electrónico',
                          hint: 'usuario@ejemplo.com',
                          keyboardType: TextInputType.emailAddress,
                          validator: _validateEmail,
                          isDark: isDark,
                          themeProvider: themeProvider,
                        ),
                        const SizedBox(height: 16),
                        _buildTextField(
                          controller: _passwordController,
                          label: 'Contraseña',
                          hint: 'Mínimo 8 caracteres',
                          obscureText: true,
                          validator: _validatePassword,
                          isDark: isDark,
                          themeProvider: themeProvider,
                        ),
                        const SizedBox(height: 16),
                        _buildTextField(
                          controller: _fullNameController,
                          label: 'Nombre completo',
                          hint: 'Juan Pérez',
                          validator: _validateFullName,
                          isDark: isDark,
                          themeProvider: themeProvider,
                        ),
                        const SizedBox(height: 16),
                        _buildTextField(
                          controller: _phoneController,
                          label: 'Teléfono (opcional)',
                          hint: '+1234567890',
                          keyboardType: TextInputType.phone,
                          isDark: isDark,
                          themeProvider: themeProvider,
                        ),
                        const SizedBox(height: 16),
                        _buildRoleDropdown(isDark, themeProvider),
                        const SizedBox(height: 32),
                        ElevatedButton(
                          onPressed: _createUser,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: themeProvider.getPrimaryColor(isDark),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          child: const Text(
                            'Crear Usuario',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
        );
      },
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    TextInputType? keyboardType,
    bool obscureText = false,
    String? Function(String?)? validator,
    required bool isDark,
    required ThemeProvider themeProvider,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      validator: validator,
      style: TextStyle(color: themeProvider.getTextColor(isDark)),
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        labelStyle: TextStyle(color: themeProvider.getTextColor(isDark)),
        hintStyle: TextStyle(color: themeProvider.getSecondaryTextColor(isDark)),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: themeProvider.getSecondaryTextColor(isDark)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: themeProvider.getSecondaryTextColor(isDark)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: themeProvider.getPrimaryColor(isDark)),
        ),
        filled: true,
        fillColor: themeProvider.getCardColor(isDark),
      ),
    );
  }

  Widget _buildRoleDropdown(bool isDark, ThemeProvider themeProvider) {
    return Consumer<UserProvider>(
      builder: (context, userProvider, child) {
        return DropdownButtonFormField<int>(
          value: _selectedRoleId,
          decoration: InputDecoration(
            labelText: 'Rol',
            labelStyle: TextStyle(color: themeProvider.getTextColor(isDark)),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: themeProvider.getSecondaryTextColor(isDark)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: themeProvider.getSecondaryTextColor(isDark)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: themeProvider.getPrimaryColor(isDark)),
            ),
            filled: true,
            fillColor: themeProvider.getCardColor(isDark),
          ),
          dropdownColor: themeProvider.getCardColor(isDark),
          style: TextStyle(color: themeProvider.getTextColor(isDark)),
          items: userProvider.roles.map((role) {
            return DropdownMenuItem<int>(
              value: role.id,
              child: Text(role.name),
            );
          }).toList(),
          onChanged: (value) {
            setState(() {
              _selectedRoleId = value;
            });
          },
          validator: (value) {
            if (value == null) {
              return 'Por favor selecciona un rol';
            }
            return null;
          },
        );
      },
    );
  }

  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'El correo electrónico es requerido';
    }
    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
      return 'Ingresa un correo electrónico válido';
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'La contraseña es requerida';
    }
    if (value.length < 8) {
      return 'La contraseña debe tener al menos 8 caracteres';
    }
    return null;
  }

  String? _validateFullName(String? value) {
    if (value == null || value.isEmpty) {
      return 'El nombre completo es requerido';
    }
    if (value.length < 2) {
      return 'El nombre debe tener al menos 2 caracteres';
    }
    return null;
  }

  void _createUser() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final userProvider = Provider.of<UserProvider>(context, listen: false);
    final success = await userProvider.createUser(
      email: _emailController.text.trim(),
      password: _passwordController.text,
      fullName: _fullNameController.text.trim(),
      phone: _phoneController.text.trim().isEmpty ? null : _phoneController.text.trim(),
      roleId: _selectedRoleId!,
    );

    setState(() {
      _isLoading = false;
    });

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Usuario creado correctamente'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pop(context, true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al crear usuario: ${userProvider.error}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}
