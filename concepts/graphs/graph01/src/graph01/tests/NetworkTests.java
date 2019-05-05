package graph01.tests;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import graph01.Network;

import org.junit.Test;

public class NetworkTests {

	@Test
	public void testCreateConnections() {
		Network network = new Network(8);
		network.connect(1, 2);
		network.connect(6, 2);
		network.connect(2, 4);
		network.connect(5, 8);
	}

	@Test
	public void testConnections() {
		Network network = new Network(8);
		network.connect(1, 2);
		network.connect(6, 2);
		network.connect(2, 4);
		network.connect(5, 8);

		assertTrue(network.query(1, 6));
		assertTrue(network.query(6, 4));
		assertFalse(network.query(7, 4));
		assertFalse(network.query(5, 6));
		assertTrue(network.query(1, 2));
	}

	@Test(expected = IllegalArgumentException.class)
	public void testInvalidSize() {
		Network network = new Network(-1);
	}

	@Test(expected = IllegalArgumentException.class)
	public void testInvalidConnection() {
		Network network = new Network(8);
		network.connect(-1, 2);
	}

	@Test(expected = IllegalArgumentException.class)
	public void testInvalidQuery() {
		Network network = new Network(-1);
		network.query(1, -1);
	}
}
