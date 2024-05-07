# Model Code Documentation

This is a document that goes over information that needs to be passed along to help me put all of the model code into a block structure. This wiki covers documentation that I need to restructure the models, the other wiki includes the format and syntax of the block code. I’ve included an example from the restore model of how to structure the information.

## 1. Sets in the Model

The name, data type, and data range of the sets in the model:

| Name          | Data Type | Description      | Range    |
|---------------|-----------|------------------|----------|
| Global_region | Range     | Range of regions | (1,26)   |
| Global_month  | Integer   | Number of months | (1,12)   |
| Global_hour   | Integer   | Number of hours  | (1,577)  |

## 2. Primary Variable

The name and data range of the primary variable in the model:

| Name                | Description                     | Set defined over                                            |
|---------------------|---------------------------------|-------------------------------------------------------------|
| Model.Generation    | Quantity of electricity generated | (ptr = generation type, y = year, r = region, steps = timesteps, hr = hour) |

## 3. Model Linkages and Parameter Exchange

The name of the parameters in the model that get exchanged with other models along with model structure of linkages:

There are several ways parameters get passed between models. In version 1 and 2, one model updates a parameter or variable and then passes it into another model as a parameter value. This second model takes this data as an input but doesn’t update the parameter. In version 3, one model updates a parameter then passes it to another model which updates and passes the parameter back. Sometimes we test scenarios trying different model structures, please include all parameters and model structure versions you’re currently using.

### Restore & Coal Model Example 1

| Name          | Description             | Model Version and linkage       | Update 1                              | Exchange 1                                          | Update 2                                          | Exchange 2  | Range Size                                       |
|---------------|-------------------------|---------------------------------|---------------------------------------|----------------------------------------------------|--------------------------------------------------|-------------|--------------------------------------------------|
| SupplyPrice   | Price of supplying electricity | 3, linked with coal model       | Does not get updated in Restore Model once initialized | Goes into each generation model as a parameter of marginal revenue | Gets updated as a dual variable once coal generation is solved for | Gets passed back to restore model once updated | (ptr = generation type, r = region, s = season, steps = timestep, y = year) |
| Generation    | Electricity generation  | 1, linked with coal model       | Updates as total generation each run  | Goes into coal model as part of generation constraint | n/a                                             | n/a         | (ptr = generation type, y = year, r = region, steps = timesteps, hr = hour) |

### Restore & Coal Model Example 2

| Name          | Description             | Model Version and linkage       | Update 1                              | Exchange 1                                          | Update 2                                          | Exchange 2  | Range Size                                       |
|---------------|-------------------------|---------------------------------|---------------------------------------|----------------------------------------------------|--------------------------------------------------|-------------|--------------------------------------------------|
| SupplyPrice   | Price of supplying electricity | 3, linked with coal model       | Does not get updated in Restore Model once initialized | Goes into each generation model as a parameter of marginal revenue | Gets updated as a dual variable once coal generation is solved for | Gets passed back to restore model once updated | (ptr = generation type, r = region, s = season, steps = timestep, y = year) |

## 4. Model Versions and Switches

If the model has several different versions which require switches on/off for different constraints and objective functions then include the following information:

| Name of Switch Variable | Switch Value | Turns on Constraints | Turns off constraints | Turns on Objective Function | Turns off Objective Function |
|-------------------------|--------------|----------------------|-----------------------|-----------------------------|------------------------------|
| Switch1                 | 0            | Constraint1          | Constraint2           | Objective1                  | Objective2                   |
| Switch1                 | 1            | Constraint2          | Constraint1           | Objective2                  | Objective1                   |
