import pandas as pd
from pandas.compat import u

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

cat_vec = list(set(feature_vec).intersection(cat))
num_vec = list(set(feature_vec).intersection(numerical))


if __name__ == "__main__":

    cat_vec = list(set(feature_vec).intersection(cat))
    num_vec = list(set(feature_vec).intersection(numerical))
    d = pd.read_csv("test.csv")
    # print d.keys()
    print d[cat_vec]
