(define (domain interplanetary_museum_domain_1)
	(:requirements :strips :typing)
	(:types
		location - object
		room - location
		carriable_item - entity
		artifact - carriable_item
		pod - carriable_item
		robot - entity
		standard_curator - robot
    )
	(:constants
		pod_pickup - location
		tunnel - location)
    (:predicates
        (at ?arg0 - entity ?arg1 - location)
		(is_not_seisming ?arg0 - location)
		(is_freezing ?arg0 - location)
		(connected ?destination - location)
		(is_vibration_free ?arg0 - location)
		(is_safe ?arg0 - artifact)
		(is_sturdy ?arg0 - artifact)
		(is_sensitive ?arg0 - artifact)
		(is_thermosensitive ?arg0 - artifact)
		(is_seismic_sensitive ?arg0 - artifact)
		(is_loaded ?arg0 - robot)
		(has_pod ?arg0 - robot ?arg1 -pod)
		(on ?arg0 - carriable_item ?arg1 - robot)
		(in ?arg0 - artifact ?arg1 - pod)
		(is_unloaded ?arg0 - robot) ;not carrying any artifact
		(is_unpodded ?arg0 - robot) ;not carrying any pod
		(pod_is_available ?arg0 - pod); available for pickup
		(pod_is_empty ?arg0 - pod); no artifact inside
		(is_sealed ?arg0 - robot)
		(is_unsealed ?arg0 - robot)
    )

	(:action pickup_standard_artifact
		:parameters (?agent - robot ?artifact - artifact ?room - room)
		:precondition (and 
			(is_unloaded ?agent)
			(is_unsealed ?agent)
			(at ?agent ?room)
			(at ?artifact ?room)
			(is_sturdy ?artifact)
		)
		:effect (and
			(not (is_unloaded ?agent))
			(not (at ?artifact ?room))
			(on ?artifact ?agent)
			(is_loaded ?agent)
		)
	)

	(:action drop_standard_artifact
		:parameters (?agent - robot ?artifact - artifact ?room - room)
		:precondition (and
			(on ?artifact ?agent)
			(at ?agent ?room)
			(is_unsealed ?agent)
			(is_loaded ?agent)
			(is_sturdy ?artifact)
		)
		:effect (and
			(not (on ?artifact ?agent))
			(not (is_loaded ?agent))
			(at ?artifact ?room)
			(is_unloaded ?agent)
			(is_safe ?artifact)
		)
	)
	(:action pickup_sensitive_artifact
		:parameters (?agent - standard_curator ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(on ?pod ?agent)
			(is_unsealed ?agent)
			(has_pod ?agent ?pod)
			(pod_is_empty ?pod)
			(is_sensitive ?artifact)
			(is_unloaded ?agent)
			(at ?agent ?room)
			(at ?artifact ?room)
		)
		:effect (and
			(not (pod_is_empty ?pod))
			(not(is_unloaded ?agent))
			(not (at ?artifact ?room))
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(is_loaded ?agent)
		)
	)

	(:action safe_drop_seismic_sensitive_artifact
		:parameters (?agent - standard_curator ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(on ?pod ?agent)
			(is_unsealed ?agent)
			(has_pod ?agent ?pod)
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(is_seismic_sensitive ?artifact)
			(is_vibration_free ?room)
			(at ?agent ?room)
			(is_loaded ?agent)
		)
		:effect (and
			(not (on ?artifact ?agent))
			(not (in ?artifact ?pod))
			(not(is_loaded ?agent))
			(at ?artifact ?room)
			(pod_is_empty ?pod)
			(is_unloaded ?agent)
			(is_safe ?artifact)
		)
	)

	(:action safe_drop_thermosensitive_artifact
		:parameters (?agent - standard_curator ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(on ?pod ?agent)
			(is_unsealed ?agent)
			(has_pod ?agent ?pod)
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(is_thermosensitive ?artifact)
			(is_freezing ?room)
			(at ?agent ?room)
			(is_loaded ?agent)
		)
		:effect (and
			(not (on ?artifact ?agent))
			(not (in ?artifact ?pod))
			(not(is_loaded ?agent))
			(at ?artifact ?room)
			(pod_is_empty ?pod)
			(is_unloaded ?agent)
			(is_safe ?artifact)
		)
	)

	(:action safe_drop_seismic_and_thermo_sensitive_artifact
		:parameters (?agent - standard_curator ?artifact - artifact ?pod - pod ?room - room)
		:precondition (and
			(on ?pod ?agent)
			(is_unsealed ?agent)
			(has_pod ?agent ?pod)
			(on ?artifact ?agent)
			(in ?artifact ?pod)
			(is_seismic_sensitive ?artifact)
			(is_thermosensitive ?artifact)
			(is_vibration_free ?room)
			(is_freezing ?room)
			(at ?agent ?room)
			(is_loaded ?agent)
		)
		:effect (and
			(not (on ?artifact ?agent))
			(not (in ?artifact ?pod))
			(not(is_loaded ?agent))
			(at ?artifact ?room)
			(pod_is_empty ?pod)
			(is_unloaded ?agent)
			(is_safe ?artifact)
		)
	)
	

	(:action move_in_room
		:parameters (?agent - standard_curator ?destination - location)
		:precondition (and
			(at ?agent tunnel)
			(is_sealed ?agent)
			(connected tunnel ?destination)
			(is_not_seisming ?destination)
		)
		:effect (and
			(not(is_sealed ?agent))
			(is_unsealed ?agent)
			(not (at ?agent tunnel))
			(at ?agent ?destination)
		)
	)

	(:action move_out_room
		:parameters (?agent - standard_curator ?departure - location)
		:precondition (and
			(at ?agent ?departure)
			(is_unsealed ?agent)
		)
		:effect (and
			(is_sealed ?agent)
			(not(is_unsealed ?agent))
			(not (at ?agent ?departure))
			(at ?agent tunnel)
		)
	)
	

	(:action take_pod
		:parameters (?agent - standard_curator ?pod - pod)
		:precondition (and
			(at ?agent pod_pickup)
			(at ?pod pod_pickup)
			(is_unsealed ?agent)
			(pod_is_empty ?pod)
			(pod_is_available ?pod)
			(is_unloaded ?agent)
			(is_unpodded ?agent)
		)
		:effect (and
			(not(at ?pod pod_pickup))
			(not(pod_is_available ?pod))
			(not(is_unpodded ?agent))
			(on ?pod ?agent)
			(has_pod ?agent ?pod)
		)
	)

	(:action drop_pod
		:parameters (?agent - standard_curator ?pod - pod)
		:precondition (and
			(at ?agent pod_pickup)
			(is_unsealed ?agent)
			(on ?pod ?agent)
			(has_pod ?agent ?pod)
			(pod_is_empty ?pod)
			(is_unloaded ?agent)
		)
		:effect (and
			(not (on ?pod ?agent))
			(not (has_pod ?agent ?pod))
			(at ?pod pod_pickup)
			(pod_is_available ?pod)
			(is_unpodded ?agent)
		)
	)
)