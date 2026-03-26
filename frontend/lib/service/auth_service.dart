import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  // 실제 서버의 API Base URL로 수정하세요
  static const String baseUrl = 'https://api.your-domain.com/v1/auth';

  // 1. 인증번호 전송 API
  static Future<bool> sendVerificationCode(String phoneNumber) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/send-sms'),
        body: jsonEncode({'phone': phoneNumber}),
        headers: {'Content-Type': 'application/json'},
      );

      return response.statusCode == 200;
    } catch (e) {
      print('인증번호 전송 에러: $e');
      return false;
    }
  }

  // 2. 인증번호 검증 API
  static Future<bool> verifyCode(String phoneNumber, String code) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/verify-sms'),
        body: jsonEncode({'phone': phoneNumber, 'code': code}),
        headers: {'Content-Type': 'application/json'},
      );

      return response.statusCode == 200;
    } catch (e) {
      print('인증번호 검증 에러: $e');
      return false;
    }
  }

  // 3. 최종 회원가입 API
  static Future<Map<String, dynamic>> signup({
    required String name,
    required String gender,
    required String phone,
    required String loginId,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/signup'),
        body: jsonEncode({
          'name': name,
          'gender': gender,
          'phone': phone,
          'login_id': loginId,
          'password': password,
        }),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return {'success': true, 'message': '가입 성공'};
      } else {
        // 에러 메시지 추출 (서버 응답 구조에 따라 다름)
        final data = jsonDecode(response.body);
        return {'success': false, 'message': data['message'] ?? '가입 실패'};
      }
    } catch (e) {
      return {'success': false, 'message': '네트워크 오류가 발생했습니다.'};
    }
  }
}