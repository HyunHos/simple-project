
import 'package:flutter/material.dart';

class CommonUtils{
  static final CommonUtils _instance = CommonUtils._();

  static CommonUtils get instance => _instance;
  static var isInit = false;

  CommonUtils._() {
    if (isInit) {
      return;
    }
    _init();
    isInit = true;
  }

  /// 초기화시 설정이 필요한 항목을 처리
  void _init() {
    print("====== CommonUtils init ==========");
  }

  void showMessage(BuildContext context, String sMsg){
    final snackBar = SnackBar(
      content: Text(sMsg),
    );

    ScaffoldMessenger.of(context).showSnackBar(snackBar);
  }
}