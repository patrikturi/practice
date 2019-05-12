package search;

public class SearchUtil {

	public static int binarySearch(int[] array, int value) {
		int low = 0;
		int high = array.length - 1;

		while (high >= low) {
			int mid = (high + low) / 2;

			if (value > array[mid]) {
				low = mid + 1;
			} else if (value < array[mid]) {
				high = mid - 1;
			} else {
				return mid;
			}
		}

		return -1;
	}
}
