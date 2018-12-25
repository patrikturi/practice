package com.callcenter;

import java.util.ArrayList;

public class DepartmentCallCenter {

	private ArrayList<Employee> freshers = new ArrayList<Employee>();
	private Employee teamLead;
	private Employee projectManager;

	public DepartmentCallCenter(Employee tl, Employee pm) {
		teamLead = tl;
		projectManager = pm;
	}

	public void handle(Call call) {
		CallHandler handler = getCallHandler();
		handler.handle(call);
	}

	public void update() {
		for (Employee employee : freshers) {
			employee.update();
		}
		teamLead.update();
		projectManager.update();
	}

	private CallHandler getCallHandler() {
		for (Employee employee : freshers) {
			if (employee.isAvailable()) {
				return employee;
			}
		}
		if (teamLead.isAvailable()) {
			return teamLead;
		}
		if (projectManager.isAvailable()) {
			return projectManager;
		}
		return AutoCallHandler.INSTANCE;
	}

	public void addFresher(Employee e) {
		freshers.add(e);
	}

	public void removeFresher(Employee e) {
		freshers.remove(e);
	}

	public void setTeamLead(Employee tl) {
		teamLead = tl;
	}

	public void setProjectManager(Employee pm) {
		projectManager = pm;
	}
}
