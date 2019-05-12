package search;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class SearchTests {

	int[] ar = new int[] { -2, 5, 6, 9, 11, 15, 20 };

	@Test
	public void testFindUpper() {
		int index = SearchUtil.binarySearch(ar, 11);
		assertEquals(4, index);
	}

	@Test
	public void testFindLower() {
		int index = SearchUtil.binarySearch(ar, -2);
		assertEquals(0, index);
	}

	@Test
	public void testTwoElements() {
		int index = SearchUtil.binarySearch(new int[] { 5, 6 }, 6);
		assertEquals(1, index);
	}

	@Test
	public void testOneElement() {
		int index = SearchUtil.binarySearch(new int[] { 3 }, 3);
		assertEquals(0, index);
	}

	@Test
	public void testNotFound() {
		int index = SearchUtil.binarySearch(new int[] { 3, 4, 5 }, 6);
		assertEquals(-1, index);
	}
}
