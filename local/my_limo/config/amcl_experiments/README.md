# AMCL experiment parameter sets

Use one file per run by copying it over `../amcl_params.yml` before launching.

Example:

```bash
cp local/my_limo/config/amcl_experiments/amcl_params_v1_update_particles.yml local/my_limo/config/amcl_params.yml
docker compose up limo_research
```

Files:
- amcl_params_baseline.yml: Current baseline from your working file.
- amcl_params_v1_update_particles.yml: More frequent updates + more beams + more particles.
- amcl_params_v2_skid_motion.yml: V1 plus increased skid-steer motion uncertainty.
- amcl_params_v3_sensor_robust.yml: V2 plus softer/robust sensor model.
- amcl_params_v4_sensor_sharp.yml: V2 plus sharper/strict sensor model.
- amcl_params_v5_recovery_enabled.yml: V2 with recovery enabled to escape wrong mode.
- amcl_params_v6_high_search.yml: Aggressive search/spread profile.
- amcl_params_v7_anchor_low_drift.yml: Strong map anchoring with low recovery and high beam usage.
- amcl_params_v8_rotation_balance.yml: Balanced rotational robustness and scan matching.
- amcl_params_v9_clutter_beamskip.yml: Enables beam skipping to reduce clutter mismatch effects.
- amcl_params_v10_yaw_trim_minus8deg.yml: Yaw A/B test using a negative trim.
- amcl_params_v11_yaw_trim_plus8deg.yml: Yaw A/B test using a positive trim.
- amcl_params_v12_dynamic_robust.yml: Softer clutter-robust sensor weighting with beamskip.
- amcl_params_v13_translation_hold.yml: Lower translation noise to reduce lateral drift.
- amcl_params_v14_slow_phase_stable.yml: Calmer updates/resampling aimed at slow-phase stability.
- amcl_params_v15_v13_rotlock.yml: V13-derived with tighter rotational lock during turning.
- amcl_params_v16_v13_mild_recovery.yml: V13-derived with very small recovery to escape wrong rotational modes.
- amcl_params_v17_v13_low_jitter.yml: V13-derived calmer profile to reduce late-phase jitter and ghost clusters.

Preferred: fill in `amcl_quick_observations.md` after each run for fast qualitative comparison.

Optional: use `amcl_experiment_observations.csv` if you want numeric tracking.
