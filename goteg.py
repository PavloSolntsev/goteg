#!/usr/bin/python

# Copyright (C) 2018 Pavlo Solntsev <pavlo.solntsev@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from string import Template
import argparse

parser = argparse.ArgumentParser(prog='GObjectGen')
parser.add_argument('-p','--parent',
                    nargs=2,
                    default=['G','Object'],
                    help='specify module and classname of the parent class. Default: G Object')
parser.add_argument('-m','--module',required=True, help='Module name, eg. Gtk, Gio.')
parser.add_argument('-o','--object',required=True, help='Object name, e.g. Button, Window')
parser.add_argument('-t','--type',choices=['final','derivable'],default='final',help='Define what type of derived object to create')
args = parser.parse_args()

htemplate_final = """/*
 * Copyright/Licensing information.
 */

#ifndef __${cmodule}_${cobject}_H__
#define __${cmodule}_${cobject}_H__

/* incude header for parent class */
#include <glib-object.h>

/* Potentially, include other headers on which this header depends */
G_BEGIN_DECLS

/* Type declaration */
#define ${cmodule}_TYPE_${cobject} ${lmodule}_${lobject}_get_type ()
G_DECLARE_FINAL_TYPE (${objectname}, ${lmodule}_${lobject}, $cmodule, $cobject, $parent)

/* Method definitions */
$objectname *${lmodule}_${lobject}_new (void);

G_END_DECLS

#endif /* __${cmodule}_${cobject}_H__ */
"""

htemplate_derivable = """/*
 * Copyright/Licensing information.
 */
#include <glib-object.h>

#ifndef __${cmodule}_${cobject}_H__
#define __${cmodule}_${cobject}_H__

/* incude header for parent class */

/* Potentially, include other headers on which this header depends */
G_BEGIN_DECLS

/* Type declaration */
#define ${cmodule}_TYPE_${cobject} ${lmodule}_${lobject}_get_type ()
G_DECLARE_DERIVABLE_TYPE (${objectname}, ${lmodule}_${lobject}, $cmodule, $cobject, $parent)

struct _${objectname}Class {
    ${parent}Class parent_class;
};

/* Method definitions */
$objectname *${lmodule}_${lobject}_new (void);

G_END_DECLS

#endif /* __${cmodule}_${cobject}_H__ */
"""
ctemplate_final = """
/* Copyright information here */
#include "$headerfile"

enum
{
    PROP_FIRSTPROP = 1,
    PROP_SECONDPROP = 2,
    N_PROPERTIES,
};

static GParamSpec *obj_properties[N_PROPERTIES] = {NULL,NULL};

struct _${objectname}
{
    $parent parent_instance;
    gchar *firstprop;
};

G_DEFINE_TYPE($objectname,${lmodule}_${lobject},${typeparent})

static void
${lmodule}_${lobject}_set_property (GObject      *object,
                          guint         property_id,
                          const GValue *value,
                          GParamSpec   *pspec)
{
    $objectname *self = ${cmodule}_${cobject} (object);

    switch (property_id) {
    case PROP_FIRSTPROP:
        g_free (self->firstprop);
        self->firstprop = g_value_dup_string (value);
        g_print ("filename: %s\\n", self->firstprop);
    break;

    default:
    /* We don't have any other property... */
        G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
    break;
    }
}

static void
${lmodule}_${lobject}_get_property (GObject    *object,
                          guint       property_id,
                          GValue     *value,
                          GParamSpec *pspec)
{
    $objectname *self = ${cmodule}_${cobject} (object);

    switch (property_id) {
    case PROP_FIRSTPROP:
        g_value_set_string (value, self->firstprop);
    break;

    default:
        /* We don't have any other property... */
        G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
    break;
    }
}

static void
${lmodule}_${lobject}_init ($objectname *self)
{
/* initialize all public and private members to reasonable default values.
 * They are all automatically initialized to 0 to begin with. 
 */
}

static void
${lmodule}_${lobject}_dispose (GObject *gobject)
{

/* In dispose(), you are supposed to free all types referenced from this
 * object which might themselves hold a reference to self. Generally,
 * the most simple solution is to unref all members on which you own a 
 * reference.
 */

/* dispose() might be called multiple times, so we must guard against
 * calling g_object_unref() on an invalid GObject by setting the member
 * NULL; g_clear_object() does this for us.
 */
 /* Always chain up to the parent class; there is no need to check if
  * the parent class implements the dispose() virtual function: it is
  * always guaranteed to do so
  */
    G_OBJECT_CLASS (${lmodule}_${lobject}_parent_class)->dispose (gobject);
}

static void
${lmodule}_${lobject}_finalize (GObject *gobject)
{
  /* Always chain up to the parent class; as with dispose(), finalize()
   * is guaranteed to exist on the parent's class virtual function table
   */
  G_OBJECT_CLASS (${lmodule}_${lobject}_parent_class)->finalize (gobject);
}

static void
${lmodule}_${lobject}_class_init (${objectname}Class *klass)
{
/* Add class initialization code here */
    GObjectClass *object_class = G_OBJECT_CLASS(klass);
    object_class->set_property = ${lmodule}_${lobject}_set_property;
    object_class->get_property = ${lmodule}_${lobject}_get_property;

    obj_properties[PROP_FIRSTPROP] =
        g_param_spec_string("Property name",
                            "Nick name for the property",
                            "Description of the property",
                            NULL /* Default value as char* */,
                            G_PARAM_READWRITE | G_PARAM_CONSTRUCT);
    obj_properties[PROP_SECONDPROP] =
        g_param_spec_string("Property name",
                            "Nick name for the property",
                            "Description of the property",
                            NULL /* Default value as char* */,
                            G_PARAM_READWRITE);

    g_object_class_install_properties(object_class,N_PROPERTIES,obj_properties);
    
    object_class->dispose = ${lmodule}_${lobject}_dispose;
    object_class->finalize = ${lmodule}_${lobject}_finalize;

}
"""

ctemplate_derivable = """
/* Copyright information here */
#include "$headerfile"

enum
{
    PROP_FIRSTPROP = 1,
    PROP_SECONDPROP = 2,
    N_PROPERTIES,
};

static GParamSpec *obj_properties[N_PROPERTIES] = {NULL,NULL};

typedef struct _${objectname}Private ${objectname}Private;

/* Private structure definition */
struct _${objectname}Private{
/* Add private members here */
    gchar *firstprop;
};

G_DEFINE_TYPE_WITH_PRIVATE($objectname,${lmodule}_${lobject},${typeparent})

static void
${lmodule}_${lobject}_set_property (GObject      *object,
                          guint         property_id,
                          const GValue *value,
                          GParamSpec   *pspec)
{
    $objectname *self = ${cmodule}_${cobject} (object);
    ${objectname}Private *priv = ${lmodule}_${lobject}_get_instance_private (self);
    
    switch (property_id) {
    case PROP_FIRSTPROP:
        g_free (priv->firstprop);
        priv->firstprop = g_value_dup_string (value);
        g_print ("filename: %s\\n", priv->firstprop);
    break;

    default:
    /* We don't have any other property... */
        G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
    break;
    }
}

static void
${lmodule}_${lobject}_get_property (GObject    *object,
                          guint       property_id,
                          GValue     *value,
                          GParamSpec *pspec)
{
    $objectname *self = ${cmodule}_${cobject} (object);
    ${objectname}Private *priv = ${lmodule}_${lobject}_get_instance_private (self);


    switch (property_id) {
    case PROP_FIRSTPROP:
        g_value_set_string (value, priv->firstprop);
    break;

    default:
        /* We don't have any other property... */
        G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
    break;
    }
}

static void
${lmodule}_${lobject}_init ($objectname *self)
{
    ${objectname}Private *priv = ${lmodule}_${lobject}_get_instance_private (self);
/* initialize all public and private members to reasonable default values.
 * They are all automatically initialized to 0 to begin with. 
 */
}

static void
${lmodule}_${lobject}_dispose (GObject *gobject)
{
    ${objectname}Private *priv = ${lmodule}_${lobject}_get_instance_private(${cmodule}_${cobject}(gobject));
/* In dispose(), you are supposed to free all types referenced from this
 * object which might themselves hold a reference to self. Generally,
 * the most simple solution is to unref all members on which you own a 
 * reference.
 */

/* dispose() might be called multiple times, so we must guard against
 * calling g_object_unref() on an invalid GObject by setting the member
 * NULL; g_clear_object() does this for us.
 */

 /* Always chain up to the parent class; there is no need to check if
  * the parent class implements the dispose() virtual function: it is
  * always guaranteed to do so
  */
    G_OBJECT_CLASS (${lmodule}_${lobject}_parent_class)->dispose (gobject);
}

static void
${lmodule}_${lobject}_finalize (GObject *gobject)
{
  ${objectname}Private *priv = ${lmodule}_${lobject}_get_instance_private (${cmodule}_${cobject}(gobject));

  g_free (NULL /* Pass pointer of private member to free */);

  /* Always chain up to the parent class; as with dispose(), finalize()
   * is guaranteed to exist on the parent's class virtual function table
   */
  G_OBJECT_CLASS (${lmodule}_${lobject}_parent_class)->finalize (gobject);
}

static void
${lmodule}_${lobject}_class_init (${objectname}Class *klass)
{
/* Add class initialization code here */
    GObjectClass *object_class = G_OBJECT_CLASS(klass);
    object_class->set_property = ${lmodule}_${lobject}_set_property;
    object_class->get_property = ${lmodule}_${lobject}_get_property;

    obj_properties[PROP_FIRSTPROP] =
        g_param_spec_string("Property name",
                            "Nick name for the property",
                            "Description of the property",
                            NULL /* Default value as char* */,
                            G_PARAM_READWRITE | G_PARAM_CONSTRUCT);
    obj_properties[PROP_SECONDPROP] =
        g_param_spec_string("Property name",
                            "Nick name for the property",
                            "Description of the property",
                            NULL /* Default value as char* */,
                            G_PARAM_READWRITE);

    g_object_class_install_properties(object_class,N_PROPERTIES,obj_properties);
    
    object_class->dispose = ${lmodule}_${lobject}_dispose;
    object_class->finalize = ${lmodule}_${lobject}_finalize;

}
"""
cmodule = args.module.upper()
lmodule = args.module.lower()
cobject = args.object.upper()
lobject = args.object.lower()
objectname = lmodule.capitalize()+lobject.capitalize()
base_filename = lmodule + '-' + lobject
hfile = base_filename + '.h'
cfile = base_filename + '.c'

parentmodule = args.parent[0].lower().capitalize()
parentclass = args.parent[1].lower().capitalize()

parent = parentmodule + parentclass
typeparent = parentmodule.upper()+'_TYPE_'+parentclass.upper()

subst = {'cmodule' : cmodule,
        'cobject' : cobject,
        'lmodule' : lmodule,
        'lobject' : lobject,
        'objectname' : objectname,
        'parent' : parent,
        'typeparent' : typeparent,
        'headerfile' : hfile}
htemplate = ''
ctemplate = ''

if args.type == 'final':
    htemplate = htemplate_final
elif args.type == 'derivable':
    htemplate = htemplate_derivable
else:
    print('This step should never be reached')
    quit()

if args.type == 'final':
    ctemplate = ctemplate_final
elif args.type == 'derivable':
    ctemplate = ctemplate_derivable
else:
    print('This step should never be reached')
    quit()

hs = Template(htemplate)
res = hs.substitute(subst)

ohfile = open(hfile,'w')
ohfile.write(res)
ohfile.close()

hs = Template(ctemplate)
res = hs.substitute(subst)

ocfile = open(cfile,'w')
ocfile.write(res)
ocfile.close()


