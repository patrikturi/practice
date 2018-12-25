package com.callcenter;

public abstract class Employee implements CallHandler {

	private boolean isAvailable = true;

	public boolean isAvailable() {
		return isAvailable;
	}

	public abstract void update();

	public abstract void hanlde(Call call);
}
