extends SceneTree
## Real scene/input regression runner; renders evidence unless --headless.

var failures: Array[String] = []
var game: Node

func check(ok: bool, message: String) -> void:
	if not ok:
		failures.append(message)
	print("CHECK ", "PASS " if ok else "FAIL ", message)

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	Input.parse_input_event(event)
	await process_frame
	await process_frame
	event.pressed = false
	Input.parse_input_event(event)
	await process_frame

func shot(name: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	await RenderingServer.frame_post_draw
	var directory := "res://production/qa/evidence/story-001-collect/"
	DirAccess.make_dir_recursive_absolute(directory)
	var error := root.get_texture().get_image().save_png(directory + name + ".png")
	check(error == OK, "screenshot " + name)

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	game = load("res://main.tscn").instantiate()
	root.add_child(game)
	await process_frame
	check(game.state == "title", "starts at title")
	await shot("01-title")
	await key(KEY_ENTER)
	await process_frame
	check(game.state == "playing", "Enter starts game via actual input")
	var initial: Vector2 = game.player
	Input.action_press("ui_right")
	for frame in range(12):
		await physics_frame
	Input.action_release("ui_right")
	check(game.player.x > initial.x, "held input moves player")
	game.player = Vector2(10000, -10000)
	await physics_frame
	await physics_frame
	check(game.player.x <= game.bounds.end.x and game.player.y >= game.bounds.position.y, "arena bounds clamp movement")
	game.player = game.spawn
	await key(KEY_P)
	await process_frame
	check(game.state == "paused", "P pauses")
	var paused: Vector2 = game.player
	Input.action_press("ui_right")
	for frame in range(6):
		await physics_frame
	Input.action_release("ui_right")
	check(game.player == paused, "paused game does not move")
	await shot("02-paused")
	await key(KEY_P)
	await process_frame
	check(game.state == "playing", "P resumes")
	var targets: Array = game.coins.duplicate()
	for point in targets:
		game.player = point
		await physics_frame
		await physics_frame
	check(game.score == targets.size() and game.state == "won", "collect all coins and win")
	await shot("03-won")
	await key(KEY_R)
	await process_frame
	check(game.state == "playing" and game.score == 0 and game.coins.size() == targets.size(), "R resets score and every coin")
	await shot("04-restarted")
	# Focus loss must not leave a moving player in a background window.
	game.notification(MainLoop.NOTIFICATION_APPLICATION_FOCUS_OUT)
	check(game.state == "paused", "focus loss auto-pauses")
	print("CYCLE_RESULT ", "PASS" if failures.is_empty() else "FAIL", " failures=", failures.size())
	game.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
