import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  // 🔥 서버 주소 (환경에 맞게 수정)
  // 안드로이드 에뮬레이터 → 10.0.2.2
  // 실제 폰 → PC IP (예: 192.168.0.10)
  static const String baseUrl = 'http://10.0.2.2:8000/api';

  static Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  // =========================================================
  // 1️⃣ 인증번호 전송
  // =========================================================
  static Future<Map<String, dynamic>> sendVerificationCode({
    required String phone,
  }) async {
    final uri = Uri.parse('$baseUrl/auth/send-code/');

    final response = await http.post(
      uri,
      headers: _headers,
      body: jsonEncode({
        'phone': phone,
      }),
    );

    return _handleResponse(response);
  }

  // =========================================================
  // 2️⃣ 인증번호 확인
  // =========================================================
  static Future<Map<String, dynamic>> verifyCode({
    required String phone,
    required String code,
  }) async {
    final uri = Uri.parse('$baseUrl/auth/verify-code/');

    final response = await http.post(
      uri,
      headers: _headers,
      body: jsonEncode({
        'phone': phone,
        'code': code,
      }),
    );

    return _handleResponse(response);
  }

  // =========================================================
  // 3️⃣ 회원가입
  // =========================================================
  static Future<Map<String, dynamic>> signup({
    required String name,
    required String gender,
    required String phone,
    required String username,
    required String password,
  }) async {
    final uri = Uri.parse('$baseUrl/auth/signup/');

    final response = await http.post(
      uri,
      headers: _headers,
      body: jsonEncode({
        'name': name,
        'gender': gender,
        'phone': phone,
        'username': username,
        'password': password,
      }),
    );

    return _handleResponse(response);
  }

  // =========================================================
  // 🔥 공통 응답 처리 (핵심)
  // =========================================================
  static Map<String, dynamic> _handleResponse(http.Response response) {
    final data = response.body.isNotEmpty
        ? jsonDecode(response.body)
        : {};

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return data;
    } else {
      throw Exception(
        data['message'] ??
            data['detail'] ??
            '서버 오류 (${response.statusCode})',
      );
    }
  }
}
