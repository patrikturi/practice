package com.callcenter;
public abstract class Call {

	private String caller;
	private int callerId;
	private boolean isOpen;

	public Call(String caller, int callerId) {
		this.caller = caller;
		this.callerId = callerId;
	}

	public String getCaller() {
		return caller;
	}

	public int getCallerId() {
		return callerId;
	}

	public boolean isOpen() {
		return isOpen;
	}

	public void open() {
		isOpen = true;
	}

	public void close() {
		isOpen = false;
	}

	public abstract String getNextMessage();

	public abstract void receiveMessage(String message);
}
