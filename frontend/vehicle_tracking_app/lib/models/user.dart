class User {
  final int id;
  final String email;
  final String fullName;
  final String? phone;
  final int roleId;
  final String? roleName;
  final bool isActive;
  final bool emailVerified;
  final DateTime? lastLogin;
  final DateTime createdAt;
  final DateTime updatedAt;

  User({
    required this.id,
    required this.email,
    required this.fullName,
    this.phone,
    required this.roleId,
    this.roleName,
    required this.isActive,
    required this.emailVerified,
    this.lastLogin,
    required this.createdAt,
    required this.updatedAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int? ?? 0,
      email: json['email'] as String? ?? '',
      fullName: json['full_name'] as String? ?? '',
      phone: json['phone'] as String?,
      roleId: json['role_id'] as int? ?? 
          ((json['role'] is Map<String, dynamic>) 
              ? ((json['role'] as Map<String, dynamic>)['id'] as int? ?? 0)
              : 0),
      roleName: (json['role'] is String) 
          ? (json['role'] as String?)
          : ((json['role'] as Map<String, dynamic>?)?['name'] as String?),
      isActive: json['is_active'] as bool? ?? true,
      emailVerified: json['email_verified'] as bool? ?? false,
      lastLogin: json['last_login'] != null 
          ? DateTime.parse(json['last_login'] as String) 
          : null,
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'phone': phone,
      'role_id': roleId,
      'role': roleName,
      'is_active': isActive,
      'email_verified': emailVerified,
      'last_login': lastLogin?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  // Helper getter for backward compatibility
  String? get role => roleName;
}
