# Copyright 2013 by Kamil Koziara. All rights reserved
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.


from Bio.Ontology.Graph import DiGraph
import copy

class OntologyGraph(DiGraph):
    """
    Represents Gene Ontology graph.
    """

    def __init__(self): #TODO add is_a to typedefs
        DiGraph.__init__(self)
        self.typedefs = {}
        self.synonyms = {}
        
    def get_node(self, u):
        x = self.nodes.get(u)
        if x is None:
            return self.synonyms.get(u)
        else:
            return x
    
    def node_exists(self, u):
        return u in self.nodes or u in self.synonyms
    
    def get_term(self, go_id):
        return self.get_node(go_id).data
    
    def get_ancestors(self, go_id):
        node = self.get_node(go_id)
        _, res = self._get_reachable(node)
        return copy.copy(res) # return copy so user won't disturb cached values

    def get_parents(self, go_id):
        node = self.get_node(go_id)
        res = set()
        for edge in node.succ:
            res.add(edge.to_node.label)
        return res
    
    def get_relationship_types(self):
        return ["is_a"] + list(self.typedefs.keys())
        
    def trim(self, relation_filter):
        """
        Returns graph with only given edges left.
        """
        
        filter_set = set(relation_filter)
        
        fgraph = OntologyGraph()
        
        for label, node in self.nodes.iteritems():
            fgraph.update_node(label, node.data)
            for edge in node.succ:
                if edge.data in filter_set:
                    fgraph.add_edge(label, edge.to_node.label, edge.data)
        
        fgraph.synonyms = dict(self.synonyms)
        for rel, typedef in self.typedefs.iteritems():
            if rel in filter_set:
                fgraph.typedefs[rel] = typedef
            
        return fgraph
    
    def get_induced_subgraph(self, nodes_ids):
        """
        Returns graph with only given nodes left
        """
        idg = super(OntologyGraph, self).get_induced_subgraph(nodes_ids)
        
        igraph = OntologyGraph()
        igraph.nodes = idg.nodes
        igraph.synonyms = copy.copy(self.synonyms)
        igraph.typedefs = copy.copy(self.typedefs)
        
        return igraph
        
class OntologyTerm(object):
    """
    Represents gene ontology term.
    """
    
    def __init__(self, nid, name, attrs = {}):
        self.id = nid
        self.name = name
        self.attrs = attrs
        
    def __str__(self):
        s = "[Term]\n"
        s += "id: " + self.id + "\n"
        s += "name: " + self.name + "\n"
        for k, v in self.attrs.iteritems():
            for vi in v:
                s+= k + ": " + vi + "\n"
        return s
            
    def __repr__(self):
        return "OntologyTerm(id = " + self.id + ", name = " + self.name + ")" 

class GeneAnnotation(object):
    """
    Represents one generic gene ontology annotation object
    """
    
    def __init__(self, oid, associations = [], attrs = {}):
        self.oid = oid
        self.associations = associations
        self.attrs = attrs
            
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return "GeneAnnotation(db_object_id = {0})".format(self.oid)
    
    def __str__(self):
        s = "DB Object ID: " + self.oid + "\n"
        for k, v in self.attrs.iteritems():
            s += k + ": " + str(v)+ "\n"       
        if len(self.associations) > 0:
            s += "\nAssociations:\n"
            for a in self.associations:
                s += str(a) + "\n"
        return s
    
class TermAssociation(object):
    """
    Represents one gene ontology term association
    """
    
    def __init__(self, go_id, attrs = {}):
        self.go_id = go_id
        self.attrs = attrs
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return "TermAssociation(go_id = {0})".format(self.go_id)
    
    def __str__(self):
        s = "GO ID: " + self.go_id + "\n"
        for k, v in self.attrs.iteritems():
            s += k + ": " + str(v) + "\n"
        return s

class GafGeneAnnotation2(object):
    """
    Represents one gene ontology annotation object
    """
    
    def __init__(self, oid, db = None, symbol = None, name = None,
                 synonyms = None, otype = None, taxon = None,
                 ext = None, gp_id = None, associations = None):
        self.db = db
        self.oid = oid
        self.symbol = symbol
        self.name = name
        self.synonyms = synonyms
        self.type = otype
        self.taxon = taxon
        
        self.ext = ext
        self.gp_id = gp_id
        
        self.associations = associations
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return "GeneAnnotation(db_object_id = {0})".format(self.oid)
    
    def __str__(self):
        b1 = """DB: {0}
DB Object ID: {1}
DB Object Symbol: {2}
DB Object Name: {3}
DB Object Synonyms: {4}
DB Object Type: {5}
Taxon: {6}
""".format(self.db, self.oid, self.symbol, self.name, self.synonyms, self.type, self.taxon)
        if self.ext != None: # only in gaf 2.0
            b1 += """Annotation Extension: {0}
Gene Product Form ID: {1}
""".format(self.ext, self.gp_id)
        if self.associations != None:
            b1 += "Associations:"
            for a in self.associations:
                b1 += str(a)
        return b1
    
class GafTermAssociation(object):
    """
    Represents one gene ontology term association
    """
    
    def __init__(self, go_id, qualifier = None, db_ref = None, evidence = None,
                 with_or_from = None, aspect = None, date = None, assigned_by = None):
        self.qualifier = qualifier
        self.go_id = go_id
        self.db_ref = db_ref
        self.evidence = evidence
        self.with_or_from = with_or_from
        self.aspect = aspect
        self.date = date
        self.assigned_by = assigned_by
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return "TermAssociation(go_id = {0})".format(self.go_id)
    
    def __str__(self):
        return """
    Qualifier: {0}
    GO ID: {1}
    DB:Reference: {2}
    Evidence Code: {3}
    With (or) From: {4}
    Aspect: {5}
    Date: {6}
    Assigned by: {7}
    """.format(self.qualifier, self.go_id, self.db_ref,\
self.evidence, self.with_or_from, self.aspect, self.date, self.assigned_by)