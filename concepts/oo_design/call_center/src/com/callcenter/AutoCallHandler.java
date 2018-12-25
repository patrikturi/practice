package com.callcenter;
public class AutoCallHandler implements CallHandler {

	public static final AutoCallHandler INSTANCE = new AutoCallHandler();

	@Override
	public void handle(Call call) {
		call.receiveMessage("Unfortunately our lines are busy. Please try again later.");
		call.close();
	}
}
