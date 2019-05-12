package merge;

public class ArrayUtil {

	/** Merge sorted arrays A and B if A has enough buffer at the end to hold B */
	public static void mergeSorted(int[] A, int[] B, int lenA) {
		// A without a buffer at the end
		int[] onlyA = new int[lenA];
		// Alias for A
		int[] dest = A;

		System.arraycopy(A, 0, onlyA, 0, lenA);

		mergeIntoOtherArray(onlyA, B, dest, lenA);
	}

	private static void mergeIntoOtherArray(int A[], int B[], int C[], int lenA) {
		int indexA = 0;
		int indexB = 0;
		int indexC = 0;

		while (indexA < lenA || indexB < B.length) {
			// Chose the array of the next element
			int[] nextSrc = null;
			int srcIndex = -1;

			if (indexA >= lenA) {
				nextSrc = B;
			} else if (indexB >= B.length) {
				nextSrc = A;
			} else {
				if (A[indexA] <= B[indexB]) {
					nextSrc = A;
				} else {
					nextSrc = B;
				}
			}

			// Copy next element into C, the source array has been selected
			if (nextSrc == A) {
				srcIndex = indexA;
				indexA++;
			} else if (nextSrc == B) {
				srcIndex = indexB;
				indexB++;
			} else {
				throw new IllegalStateException();
			}
			C[indexC] = nextSrc[srcIndex];
			indexC++;
		}
	}
}
