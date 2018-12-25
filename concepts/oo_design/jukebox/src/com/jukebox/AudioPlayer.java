package com.jukebox;

public interface AudioPlayer {

	Track load(String filePath);

	/** Play song immediately */
	void play(Track track);

	/** Queue song to be played later */
	void queue(Track track);

	boolean isPlaying();

	void stop();

	void clear();
}
