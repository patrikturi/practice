package com.jukebox;

public class Track {

	public final int id;
	public final String title;
	public final String artist;
	/** Song length in seconds */
	public final int length;

	public Track(int id, String title, String artist, int length) {
		this.id = id;
		this.title = title;
		this.artist = artist;
		this.length = length;
	}
}
