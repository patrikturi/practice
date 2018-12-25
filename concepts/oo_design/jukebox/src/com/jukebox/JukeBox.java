package com.jukebox;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/** Engine to be used with a separate UI */
public class JukeBox {

	private AudioPlayer player;
	private Cashier cashier;

	private List<Track> tracks;

	/** In dollars */
	private BigDecimal songPrice = new BigDecimal("0.5");
	/** Amount of song price already paid */
	private BigDecimal paid = BigDecimal.ZERO;
	private BigDecimal totalEarned = BigDecimal.ZERO;
	private boolean nextSongPaid = false;

	public JukeBox(AudioPlayer player, Cashier cashier) {
		this.player = player;
		this.cashier = cashier;
	}

	void load(List<String> audioFilePaths) {
		player.clear();
		tracks = new ArrayList<>();
		for (String filePath : audioFilePaths) {
			Track t = player.load(filePath);
			tracks.add(t);
		}
	}

	public List<Track> getTracks() {
		return tracks;
	}

	public Message pay(BigDecimal amount) {
		BigDecimal total = paid.add(amount);
		int compare = total.compareTo(songPrice);
		if (compare > 1) {
			cashier.giveBack(total.subtract(songPrice));
		}
		if (compare < 0) {
			paid = total;
			return Message.error("Need " + songPrice.subtract(total).toString() + "$ more.");
		}
		paid = BigDecimal.ZERO;
		totalEarned.add(songPrice);
		nextSongPaid = true;
		return Message.ok("Please select a track to be played.");
	}

	public Message playTrack(Track t) {
		if (!nextSongPaid) {
			return Message.error("Please insert " + songPrice.toString() + "$ then select a song.");
		}

		nextSongPaid = false;
		if (player.isPlaying()) {
			player.queue(t);
			return Message.ok("Queued song '" + t.title + "'.");
		}
		player.play(t);
		return Message.ok("Playing song '" + t.title + "'.");
	}

	void setPrice(BigDecimal price) {
		if (price != null) {
			songPrice = price;
		}
	}

	protected static class Message {

		public final boolean error;
		public final String text;

		protected Message(String text, boolean error) {
			this.text = text;
			this.error = error;
		}

		@Override
		public String toString() {
			if (error) {
				return "ERROR: " + text;
			}
			return text;
		}

		protected static Message error(String text) {
			return new Message(text, true);
		}

		protected static Message ok(String text) {
			return new Message(text, false);
		}
	}
}
