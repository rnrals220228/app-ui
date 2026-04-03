import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frontend/lib/model/matching_model.dart';
class ApiService {
  // 서버 주소 (본인의 서버 IP나 도메인으로 변경)
  static const String baseUrl = "http://your-backend-api.com";

  Future<void> makeMatching(MatchingRequest request) async {
    final url = Uri.parse('$baseUrl/accounts/makematching/');

    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          // 필요하다면 인증 토큰 추가: 'Authorization': 'Bearer $token',
        },
        body: jsonEncode(request.toJson()),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        // 성공 시 응답 메시지 파싱
        final data = jsonDecode(response.body);
        print("성공: ${data['message']}");
      } else {
        // 백엔드에서 에러를 보냈을 때
        print("실패: ${response.statusCode} - ${response.body}");
      }
    } catch (e) {
      // 네트워크 연결 자체의 문제일 때
      print("에러 발생: $e");
    }
  }
}