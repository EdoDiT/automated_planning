(define (domain interplanetary_museum_domain_4)
	(:requirements :strips :typing :fluents :durative-actions)
	(:types
		location - object
		entity - object
		room - location
		carriable_item - entity
		artifact - carriable_item
		pod - carriable_item
		robot - entity
		sealing_curators - robot
		standard_curator - sealing_curators
		drone_curator - robot
		tank_curator - sealing_curators
    )
	(:constants
		pod_pickup - location
		tunnel - location
		hall_beta - room)
    (:predicates
        (at ?arg0 - entity ?arg1 - location)
		(is_not_seisming ?arg0 - location)
		(is_seisming ?arg0 - location)
		(is_freezing ?arg0 - location)
		(are_connected  ?departure - location ?destination - location)
		(is_vibration_free ?arg0 - location)
		(is_safe ?arg0 - artifact)
		(is_sturdy ?arg0 - artifact)
		(is_sensitive ?arg0 - artifact)
		(is_thermosensitive ?arg0 - artifact)
		(is_seismic_sensitive ?arg0 - artifact)
		(is_thermo_and_seismic_sensitive ?arg0 - artifact)
		(has_pod ?arg0 - robot ?arg1 -pod)
		(on ?arg0 - carriable_item ?arg1 - robot)
		(in ?arg0 - artifact ?arg1 - pod)
		(pod_is_available ?arg0 - pod); available for pickup
		(pod_is_empty ?arg0 - pod); no artifact inside
		(is_sealed ?arg0 - robot)
		(is_unsealed ?arg0 - robot)
		(is_available ?arg0 - robot)
    )
	(:functions
		(capacity_available ?arg0 - robot)
		(max_capacity ?arg0 - robot)
		(pod_capacity_available ?arg0 - robot)
		(max_pod_capacity ?arg0 - robot)
		(battery_level ?arg0 - robot)
		(max_battery_level ?arg0 - robot)
		(seismic_counter)
		(seismic_phase_duration)
	)

	(:durative-action wait
		:parameters (?agent - robot)
		:duration (= ?duration 1)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) 5))
		)
	)

	(:durative-action pickup_standard_artifact
		:parameters (?agent - robot ?artifact - artifact ?room - room)
		:duration (= ?duration 1)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(at start (> (capacity_available ?agent) 0))
			(over all (is_unsealed ?agent))
			(over all (at ?agent ?room))
			(at start (at ?artifact ?room))
			(over all (is_sturdy ?artifact))
			(at start (> (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (decrease (capacity_available ?agent) 1))
			(at start (not (at ?artifact ?room)))
			(at end (on ?artifact ?agent))
		)
	)

	(:durative-action drop_standard_artifact
		:parameters (?agent - robot ?artifact - artifact ?room - room)
		:duration (= ?duration 1)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(at start (on ?artifact ?agent))
			(over all (at ?agent ?room))
			(over all (is_unsealed ?agent))
			(over all (is_sturdy ?artifact))
			(at start (> (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (not (on ?artifact ?agent)))
			(at end (increase (capacity_available ?agent) 1))
			(at end (at ?artifact ?room))
			(at end (is_safe ?artifact))
		)
	)

	(:durative-action pickup_thermosensitive_artifact
		:parameters (?agent - drone_curator ?artifact - artifact ?pod - pod ?room - room)
		:duration (= ?duration 2)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(over all (at ?agent ?room))
			(at start (> (capacity_available ?agent) 0))
			(at start (has_pod ?agent ?pod))
			(at start (pod_is_empty ?pod))
			(over all (is_sensitive ?artifact))
			(over all (is_thermosensitive ?artifact))
			(at start (> (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (at ?artifact ?room))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (decrease (capacity_available ?agent) 1))
			(at start (not (at ?artifact ?room)))
			(at end (on ?artifact ?agent))
			(at end (in ?artifact ?pod))
			(at start (not (pod_is_empty ?pod)))
		)
	)
	

	(:durative-action pickup_sensitive_artifact
		:parameters (?agent - sealing_curators ?artifact - artifact ?pod - pod ?room - room)
		:duration (= ?duration 2)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(over all (on ?pod ?agent))
			(over all (is_unsealed ?agent))
			(over all (has_pod ?agent ?pod))
			(at start (pod_is_empty ?pod))
			(over all (is_sensitive ?artifact))
			(at start (> (capacity_available ?agent) 0))
			(over all (at ?agent ?room))
			(at start (at ?artifact ?room))
			(at start (> (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (not (pod_is_empty ?pod)))
			(at start (decrease (capacity_available ?agent) 1))
			(at start (not (at ?artifact ?room)))
			(at end (on ?artifact ?agent))
			(at end (in ?artifact ?pod))
		)
	)

	(:durative-action safe_drop_seismic_sensitive_artifact
		:parameters (?agent - sealing_curators ?artifact - artifact ?pod - pod ?room - room)
		:duration (= ?duration 2)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(over all (on ?pod ?agent))
			(over all (is_unsealed ?agent))
			(over all (has_pod ?agent ?pod))
			(at start (on ?artifact ?agent))
			(at start (in ?artifact ?pod))
			(over all (is_sensitive ?artifact))
			(over all (is_seismic_sensitive ?artifact))
			(over all (is_vibration_free ?room))
			(over all (at ?agent ?room))
			(at start (> (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (not (on ?artifact ?agent)))
			(at start (not (in ?artifact ?pod)))
			(at end (increase (capacity_available ?agent) 1))
			(at end (at ?artifact ?room))
			(at end (pod_is_empty ?pod))
			(at end (is_safe ?artifact))
		)
	)

	(:durative-action safe_drop_thermosensitive_artifact
		:parameters (?agent - robot ?artifact - artifact ?pod - pod ?room - room)
		:duration (= ?duration 2)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(over all (on ?pod ?agent))
			(over all (is_unsealed ?agent))
			(over all (has_pod ?agent ?pod))
			(at start (on ?artifact ?agent))
			(at start (in ?artifact ?pod))
			(over all (is_sensitive ?artifact))
			(over all (is_thermosensitive ?artifact))
			(over all (is_freezing ?room))
			(over all (at ?agent ?room))
			(at start (> (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (not (on ?artifact ?agent)))
			(at start (not (in ?artifact ?pod)))
			(at end (at ?artifact ?room))
			(at end (pod_is_empty ?pod))
			(at end (increase (capacity_available ?agent) 1))
			(at end (is_safe ?artifact))
		)
	)

	(:durative-action safe_drop_seismic_and_thermo_sensitive_artifact
		:parameters (?agent - sealing_curators ?artifact - artifact ?pod - pod ?room - room)
		:duration (= ?duration 2)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(over all (on ?pod ?agent))
			(over all (is_unsealed ?agent))
			(over all (has_pod ?agent ?pod))
			(at start (on ?artifact ?agent))
			(at start (in ?artifact ?pod))
			(over all (is_sensitive ?artifact))
			(over all (is_thermo_and_seismic_sensitive ?artifact))
			(over all (is_vibration_free ?room))
			(over all (is_freezing ?room))
			(at start (> (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(over all (at ?agent ?room))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (not (on ?artifact ?agent)))
			(at start (not (in ?artifact ?pod)))
			(at end (at ?artifact ?room))
			(at end (pod_is_empty ?pod))
			(at end (increase (capacity_available ?agent) 1))
			(at end (is_safe ?artifact))
		)
	)
	
	(:durative-action fly
		:parameters (?agent - drone_curator ?departure - location ?destination - location)
		:duration (= ?duration 2)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(at start (at ?agent ?departure))
			(over all (are_connected ?departure ?destination))
			(at start (> (battery_level ?agent) (+ (+ 200 (* 30 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 15 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 200 (*30 (- (max_capacity ?agent) (capacity_available ?agent)))) (*15 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (not (at ?agent ?departure)))
			(at end (at ?agent ?destination))
		)
	)
	
	(:durative-action move
		:parameters (?agent - sealing_curators ?departure - location ?destination - location)
		:duration (= ?duration 4)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(at start (at ?agent ?departure))
			(over all (is_sealed ?agent))
			(over all (are_connected ?departure ?destination))
			(over all (is_not_seisming ?destination))
			(at start (> (battery_level ?agent) (+ (+ 100 (* 20 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 10 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 100 (* 20 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 10 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (not (at ?agent ?departure)))
			(at end (at ?agent ?destination))
		)
	)

	(:durative-action seal
		:parameters (?agent - sealing_curators)
		:duration (= ?duration 1)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(at start (is_unsealed ?agent))
			(at start (> (battery_level ?agent) 50))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) 50))
			(at start (not (is_unsealed ?agent)))
			(at end (is_sealed ?agent))
		)
	)

	(:durative-action unseal
		:parameters (?agent - sealing_curators)
		:duration (= ?duration 1)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(at start (is_sealed ?agent))
			(at start (> (battery_level ?agent) 50))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) 50))
			(at start (not (is_sealed ?agent)))
			(at end (is_unsealed ?agent))
		)
	)

	(:durative-action take_pod
		:parameters (?agent - robot ?pod - pod)
		:duration (= ?duration 1)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(over all (at ?agent pod_pickup))
			(at start (at ?pod pod_pickup))
			(over all (is_unsealed ?agent))
			(over all (pod_is_empty ?pod))
			(at start (pod_is_available ?pod))
			(at start (> (pod_capacity_available ?agent) 0))
			(at start (> (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (not(at ?pod pod_pickup)))
			(at start (not(pod_is_available ?pod)))
			(at start (decrease (pod_capacity_available ?agent) 1))
			(at end (on ?pod ?agent))
			(at end (has_pod ?agent ?pod))
		)
	)

	(:durative-action drop_pod
		:parameters (?agent - robot ?pod - pod)
		:duration (= ?duration 1)
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(over all (at ?agent pod_pickup))
			(over all (is_unsealed ?agent))
			(at start (on ?pod ?agent))
			(at start (has_pod ?agent ?pod))
			(over all (pod_is_empty ?pod))
			(at start (> (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (decrease (battery_level ?agent) (+ (+ 50 (* 10 (- (max_capacity ?agent) (capacity_available ?agent)))) (* 5 (- (max_pod_capacity ?agent) (pod_capacity_available ?agent))))))
			(at start (not (on ?pod ?agent)))
			(at start (not (has_pod ?agent ?pod)))
			(at end (at ?pod pod_pickup))
			(at end (pod_is_available ?pod))
			(at end (increase (pod_capacity_available ?agent) 1))
		)
	)

	(:durative-action charge_battery
		:parameters (?agent - robot)
		:duration (= ?duration (/ (- (max_battery_level ?agent) (battery_level ?agent)) 5))
		:condition (and
			(at start (is_available ?agent))
			(at start (< (seismic_counter) (seismic_phase_duration)))
			(over all (at ?agent pod_pickup))
			(over all (= (capacity_available ?agent) (max_capacity ?agent)))
			(over all (= (pod_capacity_available ?agent) (max_pod_capacity ?agent)))
			(over all (> (battery_level ?agent) 0))
		)
		:effect (and
			(at start (not (is_available ?agent)))
			(at end (is_available ?agent))
			(at start (increase (seismic_counter) 1))
			(at end (increase (battery_level ?agent) (- (max_battery_level ?agent) (battery_level ?agent))))
		)
	)

	(:action start_earthquake
		:parameters ()
		:precondition (and
			(>= (seismic_counter) (seismic_phase_duration))
		)
		:effect (and
			(is_seisming hall_beta)
			(not (is_not_seisming hall_beta))
			(assign (seismic_counter) 0)
			)
	)
	
	(:action stop_earthquake
		:parameters ()
		:precondition (and
			(>= (seismic_counter) (seismic_phase_duration))
		)
		:effect (and
			(not (is_seisming hall_beta))
			(is_not_seisming hall_beta)
			(assign (seismic_counter) 0)
		)
	)
)