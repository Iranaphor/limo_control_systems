# ROSBag Description

## Process

all 7 start with about a 8 degree to the right rotation off of the initial pose

- 2m straight forward fast

- left 90 degrees
all 7 maintain about a 8 degree to the right rotation after the turn

- 5m straight forward fast to approach the wall
v6 teleports away during this step

- left 180 degree
v1 has the worst translation error of about 80cm

- 3m straight forward fast
v6 teleports away during this step

- right 90 degrees

- 2m straight forward fast to approach opening

- right 270 degrees
during rotation, v1 overrotates on map

- 2m straight forward fast under table
translation error of about 1m left/up for baseline and v1, and 1m right/down for v2, v3, and v4

- left turn out of end of table
after this, particle spread is very large for all. baseline is aboud 55 degrees rotates, all v1-v4 are about 30 degres rotated

- curve back to middle of room
rotation drift for baseline of about 60 degrees, translation drift for v2, v3, v4 of about 2m left. v1 looks best but is still 1m drift

- curve back to start
baseline is closest but still rotation and translation drift, all have significant scattered points

The process goes on but from this point they are all either teleported away or rotated by around 45 degrees

---

## amcl_params_v7_anchor_low_drift.yml

### Q1 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q2 Rotation stability (faster turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Particle spread amount
- [ ] Too tight
- [ ] About right
- [ ] Too wide

### Q4 Particle behavior
- [ ] Single compact cluster
- [ ] Slightly multi-modal
- [ ] Frequently multi-modal

### Q5 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q6 Out-and-back consistency
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q7 End pose confidence near start
- [ ] Very high
- [ ] High
- [ ] Medium
- [ ] Low
- [ ] Very low

### Q8 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:

---

## amcl_params_v8_rotation_balance.yml

### Q1 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q2 Rotation stability (faster turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Particle spread amount
- [ ] Too tight
- [ ] About right
- [ ] Too wide

### Q4 Particle behavior
- [ ] Single compact cluster
- [ ] Slightly multi-modal
- [ ] Frequently multi-modal

### Q5 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q6 Out-and-back consistency
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q7 End pose confidence near start
- [ ] Very high
- [ ] High
- [ ] Medium
- [ ] Low
- [ ] Very low

### Q8 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:

---

## amcl_params_v9_clutter_beamskip.yml

### Q1 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q2 Rotation stability (faster turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Particle spread amount
- [ ] Too tight
- [ ] About right
- [ ] Too wide

### Q4 Particle behavior
- [ ] Single compact cluster
- [ ] Slightly multi-modal
- [ ] Frequently multi-modal

### Q5 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q6 Out-and-back consistency
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q7 End pose confidence near start
- [ ] Very high
- [ ] High
- [ ] Medium
- [ ] Low
- [ ] Very low

### Q8 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:

---

## amcl_params_v10_yaw_trim_minus8deg.yml

### Q1 Initial heading at start
- [ ] Better than before
- [ ] Same as before
- [ ] Worse than before

### Q2 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q4 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:

---

## amcl_params_v11_yaw_trim_plus8deg.yml

### Q1 Initial heading at start
- [ ] Better than before
- [ ] Same as before
- [ ] Worse than before

### Q2 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q4 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:

---

## amcl_params_v12_dynamic_robust.yml

### Q1 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q2 Rotation stability (faster turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Particle spread amount
- [ ] Too tight
- [ ] About right
- [ ] Too wide

### Q4 Particle behavior
- [ ] Single compact cluster
- [ ] Slightly multi-modal
- [ ] Frequently multi-modal

### Q5 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q6 Out-and-back consistency
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q7 End pose confidence near start
- [ ] Very high
- [ ] High
- [ ] Medium
- [ ] Low
- [ ] Very low

### Q8 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:

---

## amcl_params_v13_translation_hold.yml

### Q1 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q2 Rotation stability (faster turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Particle spread amount
- [ ] Too tight
- [ ] About right
- [ ] Too wide

### Q4 Particle behavior
- [ ] Single compact cluster
- [ ] Slightly multi-modal
- [ ] Frequently multi-modal

### Q5 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q6 Out-and-back consistency
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q7 End pose confidence near start
- [ ] Very high
- [ ] High
- [ ] Medium
- [ ] Low
- [ ] Very low

### Q8 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:

---

## amcl_params_v14_slow_phase_stable.yml

### Q1 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q2 Rotation stability (faster turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Particle spread amount
- [ ] Too tight
- [ ] About right
- [ ] Too wide

### Q4 Particle behavior
- [ ] Single compact cluster
- [ ] Slightly multi-modal
- [ ] Frequently multi-modal

### Q5 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q6 Out-and-back consistency
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q7 End pose confidence near start
- [ ] Very high
- [ ] High
- [ ] Medium
- [ ] Low
- [ ] Very low

### Q8 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:

---

## amcl_params_v15_v13_rotlock.yml

### Q1 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q2 Rotation stability (faster turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Particle spread amount
- [ ] Too tight
- [ ] About right
- [ ] Too wide

### Q4 Particle behavior
- [ ] Single compact cluster
- [ ] Slightly multi-modal
- [ ] Frequently multi-modal

### Q5 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q6 Out-and-back consistency
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q7 End pose confidence near start
- [ ] Very high
- [ ] High
- [ ] Medium
- [ ] Low
- [ ] Very low

### Q8 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:

---

## amcl_params_v16_v13_mild_recovery.yml

### Q1 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q2 Rotation stability (faster turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Particle spread amount
- [ ] Too tight
- [ ] About right
- [ ] Too wide

### Q4 Particle behavior
- [ ] Single compact cluster
- [ ] Slightly multi-modal
- [ ] Frequently multi-modal

### Q5 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q6 Out-and-back consistency
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q7 End pose confidence near start
- [ ] Very high
- [ ] High
- [ ] Medium
- [ ] Low
- [ ] Very low

### Q8 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:

---

## amcl_params_v17_v13_low_jitter.yml

### Q1 Rotation stability (slow turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q2 Rotation stability (faster turns)
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q3 Particle spread amount
- [ ] Too tight
- [ ] About right
- [ ] Too wide

### Q4 Particle behavior
- [ ] Single compact cluster
- [ ] Slightly multi-modal
- [ ] Frequently multi-modal

### Q5 Teleport/jump events
- [ ] None
- [ ] 1 minor
- [ ] Several minor
- [ ] 1 major
- [ ] Several major

### Q6 Out-and-back consistency
- [ ] Very good
- [ ] Good
- [ ] Mixed
- [ ] Poor
- [ ] Very poor

### Q7 End pose confidence near start
- [ ] Very high
- [ ] High
- [ ] Medium
- [ ] Low
- [ ] Very low

### Q8 Overall impression
- [ ] Keep for next round
- [ ] Maybe keep
- [ ] Drop

Notes:
