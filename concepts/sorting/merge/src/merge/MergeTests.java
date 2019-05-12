package merge;

import org.junit.Assert;
import org.junit.Test;

public class MergeTests {

	int[] B = new int[] { -2, 0, 6 };

	@Test
	public void testMergeSameLength() {
		int[] A = new int[] { 3, 5, 7, 0, 0, 0 };
		ArrayUtil.mergeSorted(A, B, 3);
		Assert.assertArrayEquals(new int[] { -2, 0, 3, 5, 6, 7 }, A);
	}

	@Test
	public void testMergeAShorter() {
		int[] shortA = new int[] { 3, 5, 0, 0, 0 };
		ArrayUtil.mergeSorted(shortA, B, 2);
		Assert.assertArrayEquals(new int[] { -2, 0, 3, 5, 6 }, shortA);
	}

	@Test
	public void testMergeBShorter() {
		int[] AShortB = new int[] { 3, 5, 7, 0, 0 };
		int[] shortB = new int[] { -2, 0 };
		ArrayUtil.mergeSorted(AShortB, shortB, 3);
		Assert.assertArrayEquals(new int[] { -2, 0, 3, 5, 7 }, AShortB);
	}
}
