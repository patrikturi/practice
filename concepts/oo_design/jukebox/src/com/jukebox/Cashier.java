package com.jukebox;

import java.math.BigDecimal;

public interface Cashier {

	/** Give back the change if inserted a larger coin */
	boolean giveBack(BigDecimal amount);
}
