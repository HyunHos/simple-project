import 'package:flutter/material.dart';
import 'package:mile_log/utils/CommonUtils.dart';

class MainPage extends StatelessWidget {
  const MainPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              InkWell(
                onTap: () {
                  CommonUtils.instance.showMessage(context, "test2");
                },
                child: Container(
                  color: Colors.blue,
                  width: 200,
                  height: 50,
                  child: Center(child: Text("test2")),
                ),
              ),
            ],
          )
        ),
      ),
    );
  }
}
