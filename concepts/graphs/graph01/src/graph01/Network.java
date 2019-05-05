package graph01;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Network {

	private int size;
	private Map<Integer, List<Integer>> connectionsOfElement = new HashMap<>();

	public Network(int size) {
		if (size < 0) {
			throw new IllegalArgumentException();
		}
		this.size = size;
	}

	public void connect(int first, int second) {
		validateIndices(first, second);
		Integer firstInteger = Integer.valueOf(first);
		Integer secondInteger = Integer.valueOf(second);
		List<Integer> connections;
		connections = getConnections(firstInteger);
		connections.add(secondInteger);
		connections = getConnections(secondInteger);
		connections.add(firstInteger);
	}

	public boolean query(int first, int second) {
		validateIndices(first, second);
		Integer firstInteger = Integer.valueOf(first);
		Integer secondInteger = Integer.valueOf(second);
		Set<Integer> elementsOnPath = new HashSet<>();
		return queryElement(firstInteger, secondInteger, elementsOnPath);
	}

	private boolean queryElement(Integer firstInteger, Integer secondInteger, Set<Integer> path) {

		List<Integer> connections = getConnections(firstInteger);
		if (connections.contains(secondInteger)) {
			return true;
		}

		path.add(firstInteger);
		for (Integer element : connections) {
			if (!path.contains(element)) {
				if (queryElement(element, secondInteger, path)) {
					path.remove(firstInteger);
					return true;
				}
			}
		}
		path.remove(firstInteger);
		return false;
	}

	private void validateIndices(int first, int second) {
		if (first <= 0 || first > size || second <= 0 || second > size) {
			throw new IllegalArgumentException();
		}
	}

	private List<Integer> getConnections(Integer element) {
		List<Integer> connections = connectionsOfElement.get(element);
		if (connections == null) {
			connections = new ArrayList<>();
			connectionsOfElement.put(element, connections);
		}
		return connections;
	}
}
