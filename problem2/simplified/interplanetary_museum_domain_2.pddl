(define (domain interplanetary_museum_domain_2)
	(:requirements :strips :typing :fluents)
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
		(total_cost)
	)

	(:action wait
		:parameters (?agent - robot)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 5)
		)
	)

	(:action pickup_standard_artifact
		:parameters (?agent - robot ?artifact - artifact ?room - room)
		:precondition (and 
			(< (seismic_counter) (seismic_phase_duration))
			(> (capacity_available ?agent) 0)
			(is_unsealed ?agent)
			(at ?agent ?room)
			(at ?artifact ?room)
			(is_sturdy ?artifact)
			(> (battery_level ?agent) 1)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 1)
			(decrease (capacity_available ?agent) 1)
			(not (at ?artifact ?room))
			(on ?artifact ?agent)
		)
	)

	(:action drop_standard_artifact
		:parameters (?agent - robot ?artifact - artifact ?room - room)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(on ?artifact ?agent)
			(at ?agent ?room)
			(is_unsealed ?agent)
			(is_sturdy ?artifact)
			(> (battery_level ?agent) 1)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 1)
			(not (on ?artifact ?agent))
			(increase (capacity_available ?agent) 1)
			(at ?artifact ?room)
			(is_safe ?artifact)
		)
	)

	(:action pickup_thermosensitive_artifact
		:parameters (?agent - drone_curator ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(at ?agent ?room)
			(> (capacity_available ?agent) 0)
			(has_pod ?agent ?pod)
			(pod_is_empty ?pod)
			(is_sensitive ?artifact)
			(is_thermosensitive ?artifact)
			(> (battery_level ?agent) 2)
			(at ?artifact ?room)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 1)
			(decrease (capacity_available ?agent) 2)
			(not (at ?artifact ?room))
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(not (pod_is_empty ?pod))
		)
	)
	

	(:action pickup_sensitive_artifact
		:parameters (?agent - sealing_curators ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(on ?pod ?agent)
			(is_unsealed ?agent)
			(has_pod ?agent ?pod)
			(pod_is_empty ?pod)
			(is_sensitive ?artifact)
			(> (capacity_available ?agent) 0)
			(at ?agent ?room)
			(at ?artifact ?room)
			(> (battery_level ?agent) 2)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 2)
			(not (pod_is_empty ?pod))
			(decrease (capacity_available ?agent) 1)
			(not (at ?artifact ?room))
			(on ?artifact ?agent)
			(in ?artifact ?pod)
		)
	)

	(:action safe_drop_seismic_sensitive_artifact
		:parameters (?agent - sealing_curators ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(on ?pod ?agent)
			(is_unsealed ?agent)
			(has_pod ?agent ?pod)
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(is_sensitive ?artifact)
			(is_seismic_sensitive ?artifact)
			(is_vibration_free ?room)
			(at ?agent ?room)
			(> (battery_level ?agent) 2)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 2)
			(not (on ?artifact ?agent))
			(not (in ?artifact ?pod))
			(increase (capacity_available ?agent) 1)
			(at ?artifact ?room)
			(pod_is_empty ?pod)
			(is_safe ?artifact)
		)
	)

	(:action safe_drop_thermosensitive_artifact
		:parameters (?agent - robot ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(on ?pod ?agent)
			(is_unsealed ?agent)
			(has_pod ?agent ?pod)
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(is_sensitive ?artifact)
			(is_thermosensitive ?artifact)
			(is_freezing ?room)
			(at ?agent ?room)
			(> (battery_level ?agent) 2)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 2)
			(not (on ?artifact ?agent))
			(not (in ?artifact ?pod))
			(at ?artifact ?room)
			(pod_is_empty ?pod)
			(increase (capacity_available ?agent) 1)	
			(is_safe ?artifact)
		)
	)

	(:action safe_drop_seismic_and_thermo_sensitive_artifact
		:parameters (?agent - sealing_curators ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(on ?pod ?agent)
			(is_unsealed ?agent)
			(has_pod ?agent ?pod)
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(is_sensitive ?artifact)
			(is_thermo_and_seismic_sensitive ?artifact)
			(is_vibration_free ?room)
			(is_freezing ?room)
			(> (battery_level ?agent) 2)
			(at ?agent ?room)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 2)
			(not (on ?artifact ?agent))
			(not (in ?artifact ?pod))
			(at ?artifact ?room)
			(pod_is_empty ?pod)
			(increase (capacity_available ?agent) 1)
			(is_safe ?artifact)
		)
	)
	
	(:action fly
		:parameters (?agent - drone_curator ?departure - location ?destination - location)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(at ?agent ?departure)
			(are_connected ?departure ?destination)
			(> (battery_level ?agent) 2)
		)
		:effect (and 
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 2)
			(not (at ?agent ?departure))
			(at ?agent ?destination)
		)
	)
	
	(:action move
		:parameters (?agent - sealing_curators ?departure - location ?destination - location)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(at ?agent ?departure)
			(is_sealed ?agent)
			(are_connected ?departure ?destination)
			(is_not_seisming ?destination)
			(> (battery_level ?agent) 1)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 1)
			(not (at ?agent ?departure))
			(at ?agent ?destination)
		)
	)

	(:action seal
		:parameters (?agent - sealing_curators)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(is_unsealed ?agent)
			(> (battery_level ?agent) 1)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 1)
			(not (is_unsealed ?agent))
			(is_sealed ?agent)
		)
	)

	(:action unseal
		:parameters (?agent - sealing_curators)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(is_sealed ?agent)
			(> (battery_level ?agent) 1)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 1)
			(not (is_sealed ?agent))
			(is_unsealed ?agent)
		)
	)

	(:action take_pod
		:parameters (?agent - robot ?pod - pod)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(at ?agent pod_pickup)
			(at ?pod pod_pickup)
			(is_unsealed ?agent)
			(pod_is_empty ?pod)
			(pod_is_available ?pod)
			(> (pod_capacity_available ?agent) 0)
			(> (battery_level ?agent) 1)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 1)
			(not(at ?pod pod_pickup))
			(not(pod_is_available ?pod))
			(decrease (pod_capacity_available ?agent) 1)
			(on ?pod ?agent)
			(has_pod ?agent ?pod)
		)
	)

	(:action drop_pod
		:parameters (?agent - robot ?pod - pod)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(at ?agent pod_pickup)
			(is_unsealed ?agent)
			(on ?pod ?agent)
			(has_pod ?agent ?pod)
			(pod_is_empty ?pod)
			(> (battery_level ?agent) 1)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(decrease (battery_level ?agent) 1)		
			(not (on ?pod ?agent))
			(not (has_pod ?agent ?pod))
			(at ?pod pod_pickup)
			(pod_is_available ?pod)
			(increase (pod_capacity_available ?agent) 1)
		)
	)

	(:action charge_battery
		:parameters (?agent - robot)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(at ?agent pod_pickup)
			(= (capacity_available ?agent) (max_capacity ?agent))
			(= (pod_capacity_available ?agent) (max_pod_capacity ?agent))
			(> (battery_level ?agent) 0)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(assign (battery_level ?agent) (max_battery_level ?agent))
		)
	)

	(:action start_earthquake
		:parameters ()
		:precondition (and
			(>= (seismic_counter) (seismic_phase_duration))
			(is_not_seisming hall_beta)
		)
		:effect (and
			(is_seisming hall_beta)
			(not (is_not_seisming hall_beta))
			(assign (seismic_counter) 0)
			(increase (total_cost) 1)
			)
	)
	
	(:action stop_earthquake
		:parameters ()
		:precondition (and
			(>= (seismic_counter) (seismic_phase_duration))
			(is_seisming hall_beta)
		)
		:effect (and
			(not (is_seisming hall_beta))
			(is_not_seisming hall_beta)
			(assign (seismic_counter) 0)
			(increase (total_cost) 1)
		)
	)
)