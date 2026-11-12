(define (domain interplanetary_museum_domain_2)
	(:requirements :strips :typing :fluents :negative-preconditions)
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
		(is_seisming ?arg0 - location)
		(is_freezing ?arg0 - location)
		(are_connected  ?departure - location ?destination - location)
		(is_vibration_free ?arg0 - location)
		(is_sensitive ?arg0 - artifact)
		(is_thermosensitive ?arg0 - artifact)
		(is_seismic_sensitive ?arg0 - artifact)
		(on ?arg0 - carriable_item ?arg1 - robot)
		(in ?arg0 - artifact ?arg1 - pod)
		(pod_is_available ?arg0 - pod); available for pickup
		(pod_is_empty ?arg0 - pod); no artifact inside
		(is_sealed ?arg0 - robot)
    )
	(:functions
		(capacity_available ?arg0 - robot)
		(pod_capacity_available ?arg0 - robot)
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
		)
	)

	(:action pickup_standard_artifact
		:parameters (?agent - robot ?artifact - artifact ?room - room)
		:precondition (and 
			(< (seismic_counter) (seismic_phase_duration))
			(> (capacity_available ?agent) 0)
			(not(is_sealed ?agent))
			(at ?agent ?room)
			(at ?artifact ?room)
			(not(is_sensitive ?artifact))
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
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
			(not(is_sealed ?agent))
			(not(is_sensitive ?artifact))
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(not (on ?artifact ?agent))
			(increase (capacity_available ?agent) 1)
			(at ?artifact ?room)
		)
	)

	(:action pickup_thermosensitive_artifact
		:parameters (?agent - drone_curator ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(at ?agent ?room)
			(> (capacity_available ?agent) 0)
			(on ?pod ?agent)
			(pod_is_empty ?pod)
			(is_sensitive ?artifact)
			(is_thermosensitive ?artifact)
			(not(is_seismic_sensitive ?artifact))
			(at ?artifact ?room)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
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
			(not(is_sealed ?agent))
			(pod_is_empty ?pod)
			(is_sensitive ?artifact)
			(> (capacity_available ?agent) 0)
			(at ?agent ?room)
			(at ?artifact ?room)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
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
			(not(is_sealed ?agent))
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(is_sensitive ?artifact)
			(is_seismic_sensitive ?artifact)
			(not(is_thermosensitive ?artifact))
			(is_vibration_free ?room)
			(at ?agent ?room)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(not (on ?artifact ?agent))
			(not (in ?artifact ?pod))
			(increase (capacity_available ?agent) 1)
			(at ?artifact ?room)
			(pod_is_empty ?pod)
		)
	)

	(:action safe_drop_thermosensitive_artifact
		:parameters (?agent - robot ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(on ?pod ?agent)
			(not(is_sealed ?agent))
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(is_sensitive ?artifact)
			(is_thermosensitive ?artifact)
			(not(is_seismic_sensitive ?artifact))
			(is_freezing ?room)
			(at ?agent ?room)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(not (on ?artifact ?agent))
			(not (in ?artifact ?pod))
			(at ?artifact ?room)
			(pod_is_empty ?pod)
			(increase (capacity_available ?agent) 1)
		)
	)

	(:action safe_drop_seismic_and_thermo_sensitive_artifact
		:parameters (?agent - sealing_curators ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(on ?pod ?agent)
			(not(is_sealed ?agent))
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(is_sensitive ?artifact)
			(is_thermosensitive ?artifact)
			(is_seismic_sensitive ?artifact)
			(is_vibration_free ?room)
			(is_freezing ?room)
			(at ?agent ?room)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(not (on ?artifact ?agent))
			(not (in ?artifact ?pod))
			(at ?artifact ?room)
			(pod_is_empty ?pod)
			(increase (capacity_available ?agent) 1)
		)
	)
	
	(:action fly
		:parameters (?agent - drone_curator ?departure - location ?destination - location)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(at ?agent ?departure)
			(are_connected ?departure ?destination)
		)
		:effect (and 
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
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
			(not(is_seisming ?destination))
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(not (at ?agent ?departure))
			(at ?agent ?destination)
		)
	)

	(:action seal
		:parameters (?agent - sealing_curators)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(not(is_sealed ?agent))
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(is_sealed ?agent)
		)
	)

	(:action unseal
		:parameters (?agent - sealing_curators)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(is_sealed ?agent)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(not (is_sealed ?agent))
		)
	)

	(:action take_pod
		:parameters (?agent - robot ?pod - pod)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(at ?agent pod_pickup)
			(at ?pod pod_pickup)
			(not(is_sealed ?agent))
			(pod_is_empty ?pod)
			(pod_is_available ?pod)
			(> (pod_capacity_available ?agent) 0)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(not(at ?pod pod_pickup))
			(not(pod_is_available ?pod))
			(decrease (pod_capacity_available ?agent) 1)
			(on ?pod ?agent)
		)
	)

	(:action drop_pod
		:parameters (?agent - robot ?pod - pod)
		:precondition (and
			(< (seismic_counter) (seismic_phase_duration))
			(at ?agent pod_pickup)
			(not(is_sealed ?agent))
			(on ?pod ?agent)
			(pod_is_empty ?pod)
		)
		:effect (and
			(increase (seismic_counter) 1)
			(increase (total_cost) 1)
			(not (on ?pod ?agent))
			(at ?pod pod_pickup)
			(pod_is_available ?pod)
			(increase (pod_capacity_available ?agent) 1)
		)
	)

	(:action start_earthquake
		:parameters ()
		:precondition (and
			(>= (seismic_counter) (seismic_phase_duration))
			(not (is_seisming hall_beta))
		)
		:effect (and
			(is_seisming hall_beta)
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
			(assign (seismic_counter) 0)
			(increase (total_cost) 1)
		)
	)
)