// ============================================================
// lib/screens/tabs/home_tab.dart - 홈 탭
// ============================================================
import 'package:flutter/material.dart';
import '../../utils/colors.dart';

typedef OnTabChange = void Function(int index);

class HomeTab extends StatefulWidget {
  final OnTabChange? onTabChange;
  const HomeTab({super.key, this.onTabChange});

  @override
  State<HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<HomeTab> {
  String? _activePinId;
  String? _selectedRideId;
  bool _showNotifications = false;

  final DraggableScrollableController _sheetController =
  DraggableScrollableController();

  static const _dummyPins = [
    {'id':'1','hostId':'taxi_kim', 'dept':'강남역 2번출구','dest':'김포공항',   'time':'14:30','max':4,'cur':2},
    {'id':'2','hostId':'seoul_lee','dept':'홍대입구역',    'dest':'인천공항 T1','time':'15:00','max':3,'cur':1},
    {'id':'3','hostId':'rider_park','dept':'잠실역 8번',  'dest':'강남역',      'time':'14:45','max':4,'cur':3},
    {'id':'4','hostId':'go_choi',  'dept':'신촌역',        'dest':'판교역',      'time':'16:00','max':2,'cur':0},
  ];

  static const _dummyNotifications = [
    {'icon':'🚖','msg':'taxi_kim님이 동승 요청을 수락했습니다.',       'time':'방금 전'},
    {'icon':'💬','msg':'강남→김포 팀 채팅에 새 메시지가 있습니다.',    'time':'5분 전'},
    {'icon':'📍','msg':'내 근처에 새로운 동승 핀이 생성되었습니다.',   'time':'12분 전'},
    {'icon':'✅','msg':'이용 내역이 정산되었습니다.',                   'time':'1시간 전'},
  ];

  @override
  void dispose() {
    _sheetController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                _buildHeader(),
                Expanded(child: _buildMapWithSheet()),
              ],
            ),
            if (_showNotifications) _buildNotificationOverlay(),
          ],
        ),
      ),
    );
  }

  // 헤더
  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        children: [
          RichText(text: const TextSpan(
            style: TextStyle(fontSize: 26, letterSpacing: 2, fontWeight: FontWeight.w900),
            children: [
              TextSpan(text: 'TAXI', style: TextStyle(color: AppColors.secondary)),
              TextSpan(text: 'MATE', style: TextStyle(color: AppColors.primary)),
            ],
          )),
          const Spacer(),
          // 알림 버튼
          Stack(
            children: [
              IconButton(
                icon: Icon(
                  _showNotifications ? Icons.notifications : Icons.notifications_outlined,
                  color: _showNotifications ? AppColors.primary : AppColors.secondary,
                ),
                onPressed: () => setState(() => _showNotifications = !_showNotifications),
              ),
              Positioned(
                top: 8, right: 8,
                child: Container(
                  width: 8, height: 8,
                  decoration: const BoxDecoration(color: AppColors.red, shape: BoxShape.circle),
                ),
              ),
            ],
          ),
          // 프로필 아이콘
          GestureDetector(
            onTap: () => widget.onTabChange?.call(3),  // 내 정보 탭으로 이동
            child: Container(
              width: 36, height: 36,
              decoration: BoxDecoration(
                color: AppColors.bg, shape: BoxShape.circle,
                border: Border.all(color: AppColors.border),
              ),
              child: const Icon(Icons.person, color: AppColors.gray, size: 22),
            ),
          ),
        ],
      ),
    );
  }

  // 지도 + 드래그 시트
  Widget _buildMapWithSheet() {
    return Stack(
      children: [
        GestureDetector(
          onTap: () {
            if (_activePinId != null) setState(() { _activePinId = null; _selectedRideId = null; });
            if (_showNotifications) setState(() => _showNotifications = false);
          },
          child: _buildMapArea(),
        ),
        if (_activePinId != null)
          DraggableScrollableSheet(
            controller: _sheetController,
            initialChildSize: 0.45,
            minChildSize: 0.3,
            maxChildSize: 0.85,
            snap: true,
            snapSizes: const [0.3, 0.45, 0.85],
            builder: (context, scrollController) {
              return Container(
                decoration: const BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                  boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 16, offset: Offset(0, -4))],
                ),
                child: Column(
                  children: [
                    _buildSheetHeader(),
                    Expanded(
                      child: ListView.builder(
                        controller: scrollController,
                        padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                        itemCount: _dummyPins.length,
                        itemBuilder: (_, i) => _buildRideCard(_dummyPins[i]),
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
      ],
    );
  }

  // 핀 목록
  Widget _buildSheetHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 10, 20, 12),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Column(
        children: [
          GestureDetector(
            onTap: () {
              final current = _sheetController.size;
              final targetSize = current >= 0.8 ? 0.45 : 0.95;
              _sheetController.animateTo(
                targetSize,
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeInOut,
              );
            },
            behavior: HitTestBehavior.translucent,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 60),
              child: Container(
                width: 40, height: 4,
                margin: const EdgeInsets.only(bottom: 14),
                decoration: BoxDecoration(color: AppColors.border, borderRadius: BorderRadius.circular(2)),
              ),
            ),
          ),
          Row(
            children: [
              const Text('동승 모집 목록',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppColors.secondary)),
              const SizedBox(width: 6),
              Text('${_dummyPins.length}팀', style: const TextStyle(fontSize: 12, color: AppColors.gray)),
              const Spacer(),
              GestureDetector(
                onTap: () => setState(() { _activePinId = null; _selectedRideId = null; }),
                child: const Icon(Icons.close, color: AppColors.gray, size: 20),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // 지도
  Widget _buildMapArea() {
    return SizedBox.expand(
      child: Stack(
        children: [
          Container(
            color: const Color(0xFFE8EDF2),
            child: const Center(
              child: Text('🗺️ Google Map\n(google_maps_flutter)',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: AppColors.gray, fontSize: 13)),
            ),
          ),
          ..._buildPinButtons(),
          if (_activePinId == null)
            Positioned(
              bottom: 20, left: 0, right: 0,
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: AppColors.secondary.withOpacity(0.8),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text('📍 핀을 눌러 동승 목록 확인',
                      style: TextStyle(color: Colors.white, fontSize: 12)),
                ),
              ),
            ),
        ],
      ),
    );
  }

  List<Widget> _buildPinButtons() {
    final pinPositions = [
      {'pin': _dummyPins[0], 'x': 0.44, 'y': 0.40},
      {'pin': _dummyPins[1], 'x': 0.22, 'y': 0.28},
      {'pin': _dummyPins[2], 'x': 0.65, 'y': 0.55},
      {'pin': _dummyPins[3], 'x': 0.18, 'y': 0.50},
    ];
    final size = MediaQuery.of(context).size;

    return pinPositions.map((p) {
      final pin = p['pin'] as Map<String, dynamic>;
      final isActive = _activePinId == pin['id'];
      final isFull = (pin['cur'] as int) >= (pin['max'] as int);
      return Positioned(
        left: size.width * (p['x'] as double) - 32,
        top: size.height * 0.6 * (p['y'] as double),
        child: GestureDetector(
          onTap: () => setState(() {
            _activePinId = isActive ? null : pin['id'] as String;
            _selectedRideId = null;
          }),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: isFull ? AppColors.gray : (isActive ? AppColors.primaryDark : AppColors.primary),
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(12), topRight: Radius.circular(12),
                    bottomRight: Radius.circular(12), bottomLeft: Radius.circular(2),
                  ),
                  border: Border.all(
                      color: isActive ? AppColors.accent : Colors.transparent, width: 2),
                  boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.2), blurRadius: 8, offset: const Offset(0, 3))],
                ),
                child: Text('🚖 ${pin['cur']}/${pin['max']}',
                    style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
              ),
              Container(width: 2, height: 8, color: isFull ? AppColors.gray : AppColors.primary),
            ],
          ),
        ),
      );
    }).toList();
  }

  // 동승 카드
  Widget _buildRideCard(Map<String, dynamic> pin) {
    final isSelected = _selectedRideId == pin['id'];
    final isFull = (pin['cur'] as int) >= (pin['max'] as int);
    return GestureDetector(
      onTap: () => setState(() => _selectedRideId = isSelected ? null : pin['id'] as String),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primaryLight : Colors.white,
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.border,
            width: isSelected ? 1.5 : 1,
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 44, height: 44,
                  decoration: BoxDecoration(
                    color: AppColors.bg, shape: BoxShape.circle,
                    border: Border.all(color: AppColors.border),
                  ),
                  child: const Icon(Icons.person, color: AppColors.gray, size: 26),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('@${pin['hostId']}',
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.secondary)),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Flexible(child: Text('${pin['dept']}',
                              style: const TextStyle(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.w600),
                              overflow: TextOverflow.ellipsis)),
                          const Padding(
                            padding: EdgeInsets.symmetric(horizontal: 4),
                            child: Text('→', style: TextStyle(color: AppColors.textSub, fontWeight: FontWeight.w700)),
                          ),
                          Flexible(child: Text('${pin['dest']}',
                              style: const TextStyle(fontSize: 12, color: AppColors.secondary),
                              overflow: TextOverflow.ellipsis)),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),

                // 출발 시간 강조 박스
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppColors.primary, borderRadius: BorderRadius.circular(10),
                  ),
                  child: Column(
                    children: [
                      const Text('출발', style: TextStyle(fontSize: 9, color: Colors.white70)),
                      Text('${pin['time']}',
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Colors.white)),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                ...List.generate(pin['max'] as int, (j) => Container(
                  width: 22, height: 22,
                  margin: const EdgeInsets.only(right: 4),
                  decoration: BoxDecoration(
                    color: j < (pin['cur'] as int) ? AppColors.primary : AppColors.bg,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: j < (pin['cur'] as int) ? AppColors.primary : AppColors.border),
                  ),
                  child: j < (pin['cur'] as int)
                      ? const Icon(Icons.person, color: Colors.white, size: 13)
                      : null,
                )),
                const SizedBox(width: 6),
                Text('${pin['cur']}/${pin['max']}명', style: const TextStyle(fontSize: 11, color: AppColors.gray)),
                if (isFull)
                  Container(
                    margin: const EdgeInsets.only(left: 6),
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(color: AppColors.bg, borderRadius: BorderRadius.circular(100)),
                    child: const Text('마감', style: TextStyle(fontSize: 10, color: AppColors.gray, fontWeight: FontWeight.w700)),
                  ),
              ],
            ),
            AnimatedSize(
              duration: const Duration(milliseconds: 220),
              child: isSelected ? Column(
                children: [
                  const SizedBox(height: 12),
                  const Divider(height: 1, color: AppColors.border),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: isFull ? AppColors.gray : AppColors.primary,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        elevation: 0,
                      ),
                      onPressed: isFull ? null : () {},
                      child: Text(isFull ? '마감된 팀입니다' : '참여하기',
                          style: const TextStyle(fontWeight: FontWeight.w700)),
                    ),
                  ),
                ],
              ) : const SizedBox.shrink(),
            ),
          ],
        ),
      ),
    );
  }

  // 알림 패널
  Widget _buildNotificationOverlay() {
    return Positioned(
      top: 0, right: 12, left: 12,
      child: Material(
        elevation: 8,
        borderRadius: BorderRadius.circular(16),
        color: Colors.white,
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 14, 8, 10),
                child: Row(
                  children: [
                    const Text('알림', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                    const Spacer(),
                    TextButton(
                      onPressed: () {},
                      style: TextButton.styleFrom(foregroundColor: AppColors.gray),
                      child: const Text('모두 읽음', style: TextStyle(fontSize: 11)),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 18, color: AppColors.gray),
                      onPressed: () => setState(() => _showNotifications = false),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1, color: AppColors.border),
              ..._dummyNotifications.map((n) => InkWell(
                onTap: () => setState(() => _showNotifications = false),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(n['icon']!, style: const TextStyle(fontSize: 20)),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(n['msg']!, style: const TextStyle(fontSize: 13, color: AppColors.secondary)),
                            const SizedBox(height: 2),
                            Text(n['time']!, style: const TextStyle(fontSize: 11, color: AppColors.gray)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              )),
              const SizedBox(height: 4),
            ],
          ),
        ),
      ),
    );
  }
}