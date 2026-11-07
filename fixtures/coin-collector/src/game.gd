extends Node2D
## Small, data-driven game used to verify the studio lifecycle.

var state := "title"
var score := 0
var player := Vector2.ZERO
var spawn := Vector2.ZERO
var coins: Array[Vector2] = []
var bounds := Rect2()
var tuning: Dictionary

func _ready() -> void:
	tuning = JSON.parse_string(FileAccess.get_file_as_string("res://tuning.json"))
	var box: Array = tuning.bounds
	bounds = Rect2(box[0], box[1], box[2] - box[0], box[3] - box[1])
	spawn = Vector2(tuning.spawn[0], tuning.spawn[1])
	reset_game()
	state = "title"
	RenderingServer.set_default_clear_color(Color("101a2b"))

## Reset every gameplay value without reloading external resources.
func reset_game() -> void:
	player = spawn
	score = 0
	coins.clear()
	for point in tuning.coins:
		coins.append(Vector2(point[0], point[1]))
	state = "playing"
	queue_redraw()

func _input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	if event.keycode == KEY_ENTER and state == "title":
		state = "playing"
	elif event.keycode == KEY_R and state != "title":
		reset_game()
	elif event.keycode == KEY_P or event.keycode == KEY_ESCAPE:
		if state == "playing":
			state = "paused"
		elif state == "paused":
			state = "playing"
	queue_redraw()

func _notification(what: int) -> void:
	if what == MainLoop.NOTIFICATION_APPLICATION_FOCUS_OUT and state == "playing":
		state = "paused"
		queue_redraw()

func _physics_process(delta: float) -> void:
	if state != "playing":
		return
	var movement := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	player += movement * float(tuning.speed) * delta
	player = player.clamp(bounds.position, bounds.end)
	for index in range(coins.size() - 1, -1, -1):
		if player.distance_to(coins[index]) <= float(tuning.pickup_distance):
			coins.remove_at(index)
			score += 1
	if coins.is_empty():
		state = "won"
	queue_redraw()

func text(at: Vector2, content: String, size: int, color := Color.WHITE) -> void:
	draw_string(ThemeDB.fallback_font, at, content, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)

func _draw() -> void:
	if tuning == null or tuning.is_empty():
		return
	text(Vector2(36, 52), "COIN COLLECTOR", 30, Color("6de3ce"))
	text(Vector2(36, 85), "Collect all three. A small Codex studio test game.", 19)
	text(Vector2(36, 116), "Coins: %d / %d" % [score, tuning.coins.size()], 20)
	draw_style_box(arena_style(), Rect2(18, 128, 764, 410))
	for coin in coins:
		draw_circle(coin, float(tuning.coin_radius), Color("ffd166"))
		draw_circle(coin, float(tuning.coin_radius) - 4, Color("a97825"), false, 2)
	draw_circle(player, float(tuning.player_radius), Color("6de3ce"))
	text(Vector2(36, 574), "Arrow keys: move    P / Esc: pause    R: restart", 19, Color("b4c4da"))
	if state != "playing":
		draw_rect(Rect2(140, 232, 520, 126), Color("101a2b"))
		var heading := "Ready to collect?" if state == "title" else ("You collected them all!" if state == "won" else "Paused")
		var hint := "Press Enter to start" if state == "title" else ("Press R to play again" if state == "won" else "Press P or Esc to resume")
		text(Vector2(174, 280), heading, 28)
		text(Vector2(174, 322), hint, 22, Color("6de3ce"))

func arena_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color("1b2a41")
	style.border_color = Color("344b69")
	style.set_border_width_all(2)
	style.set_corner_radius_all(16)
	return style
