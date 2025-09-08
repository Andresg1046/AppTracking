import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/user_provider.dart';
import '../../models/user.dart';

class EditUserScreen extends StatefulWidget {
  final User user;

  const EditUserScreen({super.key, required this.user});

  @override
  State<EditUserScreen> createState() => _EditUserScreenState();
}

class _EditUserScreenState extends State<EditUserScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _emailController;
  late TextEditingController _fullNameController;
  late TextEditingController _phoneController;
  
  int? _selectedRoleId;
  bool? _isActive;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController(text: widget.user.email);
    _fullNameController = TextEditingController(text: widget.user.fullName);
    _phoneController = TextEditingController(text: widget.user.phone ?? '');
    _selectedRoleId = widget.user.roleId;
    _isActive = widget.user.isActive;
    
    // Cargar roles al inicializar
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final userProvider = Provider.of<UserProvider>(context, listen: false);
      userProvider.loadRoles();
    });
  }

  @override
  void dispose() {
    _emailController.dispose();
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
              'Editar Usuario',
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
                        const SizedBox(height: 16),
                        _buildActiveSwitch(isDark, themeProvider),
                        const SizedBox(height: 32),
                        ElevatedButton(
                          onPressed: _updateUser,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: themeProvider.getPrimaryColor(isDark),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          child: const Text(
                            'Actualizar Usuario',
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
    String? Function(String?)? validator,
    required bool isDark,
    required ThemeProvider themeProvider,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
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

  Widget _buildActiveSwitch(bool isDark, ThemeProvider themeProvider) {
    return Card(
      color: themeProvider.getCardColor(isDark),
      child: SwitchListTile(
        title: Text(
          'Usuario Activo',
          style: TextStyle(color: themeProvider.getTextColor(isDark)),
        ),
        subtitle: Text(
          _isActive == true ? 'El usuario puede acceder al sistema' : 'El usuario no puede acceder al sistema',
          style: TextStyle(color: themeProvider.getSecondaryTextColor(isDark)),
        ),
        value: _isActive ?? true,
        onChanged: (value) {
          setState(() {
            _isActive = value;
          });
        },
        activeColor: themeProvider.getPrimaryColor(isDark),
      ),
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

  String? _validateFullName(String? value) {
    if (value == null || value.isEmpty) {
      return 'El nombre completo es requerido';
    }
    if (value.length < 2) {
      return 'El nombre debe tener al menos 2 caracteres';
    }
    return null;
  }

  void _updateUser() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final userProvider = Provider.of<UserProvider>(context, listen: false);
    final success = await userProvider.updateUser(
      id: widget.user.id,
      email: _emailController.text.trim(),
      fullName: _fullNameController.text.trim(),
      phone: _phoneController.text.trim().isEmpty ? null : _phoneController.text.trim(),
      roleId: _selectedRoleId!,
      isActive: _isActive,
    );

    setState(() {
      _isLoading = false;
    });

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Usuario actualizado correctamente'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pop(context, true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al actualizar usuario: ${userProvider.error}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}
