###
#6번
library(leaps)

X=data.frame(matrix(rnorm(9000),nrow=100,ncol=90))
dim(X)


attach(X)
fit.lm=lm(X1~.,data=X)


library(MASS)
fit.step=stepAIC(fit.lm,trace=FALSE)

#a
summary(fit.lm)
#b
summary(fit.step)

#c
typeof(X$X1)

x1= X[1:50,1:10]
attach(x1)
head(x1)

fit.lm1=lm(X1~.,x1)

summary(fit.lm1)


fit.step1=stepAIC(fit.lm1,trace = FALSE)
summary(fit.step1)

###

#7번
library(mlbench)

data("Vehicle")
data("Ionosphere")
data("BreastCancer")
head(Vehicle)
Vehicle$Class
dim(Vehicle)
#a
pairs(~.,data = Vehicle, pch=c(1,2,3,4)[Vehicle$Class])

head(Ionosphere)
Ionosphere$Class
pairs(Ionosphere[,1:34],data = Ionosphere, pch=c(1,2)[Ionosphere$Class])


head(BreastCancer)
BreastCancer$Class
pairs(BreastCancer[2:10],data = BreastCancer, pch=c(1,2)[BreastCancer$Class])


library(MASS)
#b
#LDA

dim(Vehicle)
colnames(Vehicle)


levels(Vehicle$Class)

  
  #idx=matrix(rep('blank',50),50,1)
idx <- sample(x = c("train", "test"), size = nrow(Vehicle), replace = TRUE, prob = c(7, 3))
train <- Vehicle[idx == "train", ] 

test <- Vehicle[idx == "test", ]
test_x <- test[, -18]

test_y <- test[, 18]




ld <- lda(formula = Class ~ ., data = train)
ld
predict(ld, test)$class
predict(ld, test)$posterior
#정오분류표
tt <- table(test$Class, predict(ld, test)$class)
tt

#정분류율 및 오불류율 계산
#lc=matrix(rep(0,50),50,1)
sum(tt[row(tt) == col(tt)])/sum(tt) #정분류율
#lw=matrix(rep(0,50),50,1)
1-sum(tt[row(tt) == col(tt)])/sum(tt) #오분류율


## QDA
qd <- qda(formula = Class ~ ., data = train)
qd

predict(qd, test)$class
predict(qd, test)$posterior

#정오분류표 작성
qtt <- table(test$Class, predict(qd, test)$class)
qtt

#정분류율 및 오불류율 계산
sum(qtt[row(qtt) == col(qtt)])/sum(qtt) #정분류율
1-sum(qtt[row(qtt) == col(qtt)])/sum(qtt) #오분류율

#logistic
logit<-glm(Class~.,data=Vehicle,family=binomial())
predict(logit,test)
ltt= table(test$Class, predict(logit, test))
ltt
sum(ltt[row(ltt) == col(ltt)])/sum(ltt) #정분류율
1-sum(ltt[row(ltt) == col(ltt)])/sum(ltt) #오분류율

#c
# k-fold cross valdiation

library(lars)
cv.log = function(yy, xx, K=10)
{
  cverr = rep(0,K)
  folder = cv.folds(length(yy),K)
  for(k in 1:K)
  {
    xx = as.matrix(xx)
    gg = glm(yy[-folder[[k]]]~xx[-folder[[k]],],family=binomial)
    pyy = cbind(1,xx[folder[[k]],])%*%gg$coef
    pyy = exp(pyy)/(1+exp(pyy))
    po = which(pyy>=0.5);pyy[po]=1;pyy[-po]=0
    cverr[k] = sum(abs(pyy-yy[folder[[k]]]))/length(yy[folder[[k]]])
  }
  return(cverr)
}

select.var = c();full.var = colnames(Vehicle)[-ncol(Vehicle)] 

cv.err = 1
for(i in 1:18)
{
  cv.err.tmp = c()
  for(j in 1:length(full.var))
  {
    cv.err.tmp[j] = mean(cv.log(Vehicle[,19],Vehicle[,c(select.var,full.var[j])]),K=20)
  }
  select.var[i] = full.var[which.min(cv.err.tmp)]
  full.var = full.var[-which.min(cv.err.tmp)]
  print(select.var);print(min(cv.err.tmp))
  if(cv.err<=min(cv.err.tmp))
    break
  cv.err = min(cv.err.tmp)
}
library(caret)


createFolds(Vehicle$Class,k=10)

  
