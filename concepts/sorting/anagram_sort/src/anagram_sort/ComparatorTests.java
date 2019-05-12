package anagram_sort;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import java.util.Arrays;
import java.util.Comparator;

import org.junit.Test;

public class ComparatorTests {

	Comparator<String> comparator = new AnagramComparator();

	@Test
	public void testSort() {
		String[] ar = new String[] { "Joe", "Kate", "Anna", "Tom" };
		Arrays.sort(ar, comparator);
		assertArrayEquals(new String[] { "Anna", "Joe", "Kate", "Tom" }, ar);
	}

	@Test
	public void testCompareEquals() {
		assertEquals(0, comparator.compare("Ab", "Acd"));
	}

}
