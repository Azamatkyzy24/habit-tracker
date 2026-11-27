export default {
	// ---------- settings and sample data (fictional) ----------
	MAX_NAME_LENGTH: 50,
	SAMPLE_HABITS: [{ name: "Read 20 pages", created: "2026-11-20", checkins: [] }],

	// ---------- date helpers ----------
	fmt(d) {
		return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
	},
	todayStr() {
		return this.fmt(new Date());
	},
	addDays(iso, n) {
		const p = iso.split("-").map(Number);
		return this.fmt(new Date(p[0], p[1] - 1, p[2] + n));
	},

	// ---------- 1. input validation ----------
	validateName(raw) {
		const name = (raw || "").trim();
		if (name === "") throw new Error("Habit name must not be empty");
		if (name.length > this.MAX_NAME_LENGTH) throw new Error("Habit name must be at most " + this.MAX_NAME_LENGTH + " characters");
		return name;
	},
	parseDate(raw, today) {
		const text = (raw || "").trim();
		if (text === "") return today; // empty field = today
		const bad = "Invalid date '" + raw + "' - use YYYY-MM-DD";
		if (!/^\d{4}-\d{2}-\d{2}$/.test(text)) throw new Error(bad);
		const p = text.split("-").map(Number);
		if (this.fmt(new Date(p[0], p[1] - 1, p[2])) !== text) throw new Error(bad); // e.g. 2026-13-01, 2026-02-30
		if (text > today) throw new Error("Date " + text + " is in the future");
		return text;
	},

	// ---------- 2. core logic (rules) ----------
	checkIn(habits, name, day) {
		const habit = habits.find(h => h.name === name);
		if (!habit) throw new Error("No habit called '" + name + "'");
		if (habit.checkins.includes(day)) throw new Error("Already checked in '" + name + "' for " + day);
		habit.checkins.push(day);
		return habit;
	},
	streak(habit, today) {
		let count = 0;
		let d = today;
		while (habit.checkins.includes(d)) {
			count += 1;
			d = this.addDays(d, -1);
		}
		return count;
	},
	weekly(habit, today) {
		const start = this.addDays(today, -6);
		const days = new Set(habit.checkins.filter(c => c >= start && c <= today));
		return Math.round(days.size / 7 * 100);
	},

	// ---------- 3. user-facing output ----------
	successText(habit, day, today) {
		return "Checked in '" + habit.name + "' for " + day + " - streak: " + this.streak(habit, today) + " days, this week: " + this.weekly(habit, today) + "%";
	},
	tableRows() {
		const today = this.todayStr();
		return (appsmith.store.habits || []).map(h => ({
			name: h.name,
			checkins: h.checkins.slice().sort().join(", "),
			streak: this.streak(h, today),
			week: this.weekly(h, today) + "%"
		}));
	},

	// ---------- button actions ----------
	async run() {
		const today = this.todayStr();
		try {
			const name = this.validateName(NameInput.text);           // 1. validation
			const day = this.parseDate(DateInput.text, today);
			const habits = JSON.parse(JSON.stringify(appsmith.store.habits || []));
			const habit = this.checkIn(habits, name, day);            // 2. core logic
			await storeValue("habits", habits, true);                 // save (only on success)
			await storeValue("result", { ok: true, text: this.successText(habit, day, today) }, true); // 3. output
		} catch (e) {
			await storeValue("result", { ok: false, text: "error: " + e.message }, true);             // 3. output (error)
		}
	},
	async resetData() {
		await storeValue("habits", JSON.parse(JSON.stringify(this.SAMPLE_HABITS)), true);
		await storeValue("result", { ok: true, text: "Sample data loaded" }, true);
	}
}
