import pandas as pd
from pandas.compat import u
from collections import OrderedDict

keys= [
  "Unique Id",
  "Category",
  "Brand",
  "Name",
  "Image URL",
  "Link URL",
  "Price (inc VAT)",
  "Manufacturer",
  "Shipping Cost",
  "Min Delivery (Days)",
  "Max Delivery (Days)",
  "Discount"
]
numerical = [
    "Unique Id",
    "Category",
    "Price (inc VAT)",
    "Shipping Cost",
    "Min Delivery (Days)",
    "Max Delivery (Days)",
    "Discount"
 ]

cat = [
     "Category",
     "Brand",
     "Name",
     "Image URL",
     "Link URL",
     "Manufacturer",
]

feature_vec = [
   "Category",
   "Brand",
   "Price (inc VAT)",
   "Manufacturer",
   "Shipping Cost",
   "Min Delivery (Days)",
   "Max Delivery (Days)",
   "Discount"
]

cat2 = [
     "category",
     "brand",
     "Name",
     "image_url",
     "url",
     "manu",
]

numerical2 = [
    "sku",
    "price",
    "shipping",
    "mindev",
    "maxdev",
    "discount"
 ]

feature_vec2 = [
   "category",
   "brand",
   "price",
   "manu",
   "shipping",
   "mindev",
   "maxdev",
   "discount"
]

cat_vec = list(set(feature_vec).intersection(cat))
num_vec = list(set(feature_vec).intersection(numerical))

cat_vec2 = list(set(feature_vec2).intersection(cat2))
num_vec2 = list(set(feature_vec2).intersection(numerical2))

conv_cat = dict(zip(cat_vec, cat_vec2))
conv_num = dict(zip(num_vec, num_vec2))



init_dat = pd.read_csv("project/test.csv")
catz = map( set, dict(init_dat[cat_vec]).values())
# cat_vec labels the rows of the cathegory matrix
cat_matrix = map(lambda x: [0]*len(x) , catz)


cats1 = map( set, dict(init_dat[cat_vec]).values())
cat_dics = map(dict, (map(lambda x: zip(range(len(x)), x) , cats1)) )
cat_dics =  OrderedDict(zip(cat_vec2, cat_dics))


if __name__ == "__main__":

    cat_vec = list(set(feature_vec).intersection(cat))
    num_vec = list(set(feature_vec).intersection(numerical))
    d = pd.read_csv("test.csv")
    # print d.keys()
    print d[cat_vec]
