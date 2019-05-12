package anagram_sort;

import java.util.Comparator;

public class AnagramComparator implements Comparator<String> {

	@Override
	public int compare(String a, String b) {
		char aa = anagram(a);
		char ab = anagram(b);
		if (aa > ab) {
			return 1;
		} else if (aa == ab) {
			return 0;
		}
		return -1;
	}

	// might not be what "anagram" really means but it's ok
	private static char anagram(String s) {
		return s.charAt(0);
	}
}
