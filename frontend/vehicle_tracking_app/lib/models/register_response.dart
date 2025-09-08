class RegisterResponse {
  final String message;
  final String role;
  final bool isFirstUser;

  RegisterResponse({
    required this.message,
    required this.role,
    required this.isFirstUser,
  });

  factory RegisterResponse.fromJson(Map<String, dynamic> json) {
    return RegisterResponse(
      message: json['message'] as String? ?? '',
      role: json['role'] as String? ?? '',
      isFirstUser: json['is_first_user'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'role': role,
      'is_first_user': isFirstUser,
    };
  }
}
