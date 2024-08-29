#2018380615 이지은 빅데이터

setwd("C:/Users/USER/Downloads")#평소 실행
setwd("D:/데이터 마이닝 방법론")#usb
diabetes=read.csv("datasets_4511_6897_diabetes.csv")

#다중 로지스틱 회귀
set.seed(619)
tr.idx=sample(1:nrow(diabetes),0.5*nrow(diabetes))#5:5으로 자료 분할
dia.train=diabetes[tr.idx,]
dia.test=diabetes[-tr.idx,]
#dia.train[,-9] <- scale(dia.train[,-9])#단위 표준화
#summary(dia.train)
#dia.train

library(boot)
train.fit=glm(Outcome~.,data=dia.train,family = "binomial")  

summary(train.fit)

test.fit=glm(Outcome~.,data=dia.test,family = "binomial")  
summary(test.fit)

library(ElemStatLearn)
backtrain.aic=step(train.fit,lpsa~1,direction = "backward") 
backtrain.bic=step(train.fit,lpsa~1,direction = "backward",k=log(nrow(dia.train))) 
#사용할 변수는 Pregnancies,Glucose,DiabetesPedigreeFunstion,BMI,BloodPressure 
diapred = predict(train.fit, dia.test[,-9], type='response')
diapred
pred_yn = ifelse(diapred>0.5, '1', '0')
table(pred_yn)
yn_mat = table(dia.test$Outcome, pred_yn, dnn=c('actual','predicted'))
yn_mat
1-sum(diag(yn_mat))/sum(yn_mat)#변수선택 이전 오분류율
#변수 선택
dia.train=dia.train[,-c(4,5,8)]
dia.test=dia.test[,-c(4,5,8)]


train.fit=glm(Outcome~.,data=dia.train,family = "binomial")  
summary(train.fit)
test.fit=glm(Outcome~.,data=dia.test,family = "binomial")  
summary(test.fit)

diapred = predict(train.fit, dia.test, type='response')

pred_yn = ifelse(diapred>0.5, '1', '0')
yn_mat = table(dia.test$Outcome, pred_yn, dnn=c('actual','predicted'))

yn_mat
       
1-sum(diag(yn_mat))/sum(yn_mat)#변수선택 이후 오분류율
library(ROCR)
a=predict(backtrain.aic)
ROC.glm = performance(prediction(a, dia.train$Outcome),"tpr","fpr")
plot(ROC.glm,main="로지스틱 회귀 ROC 곡선")



 
#의사 결정 나무
library(MASS)
library(tree)
dia.tree=tree(Outcome~.,data = dia.train)
summary(dia.tree)
dia.tree

plot(dia.tree)#전처리 전

text(dia.tree)

dia.tree1=snip.tree(dia.tree,nodes = c(3,14,7,11))
dia.tree1
plot(dia.tree1)#전처리 후
text(dia.tree1)
dia.tree1

tpred=predict(dia.tree1,dia.test[,-6],type="vector")
pred_yn = ifelse(tpred>0.5, '1', '0')

table(pred_yn)
yn_mat = table(dia.test$Outcome, pred_yn, dnn=c('actual','predicted'))
yn_mat
1-sum(diag(yn_mat))/sum(yn_mat)#오분류율


b=predict(dia.tree1)
ROC.tree = performance(prediction(b, dia.train$Outcome),"tpr","fpr")
plot(ROC.tree,main="의사결정나무 ROC곡선")


#단순 베이즈 분류
library(e1071)
dia.model=naiveBayes(as.factor(Outcome)~.,data=dia.train,laplace = 3)
pred=predict(dia.model,dia.test[,-6])
pred
table(pred,dia.test[,6]) #오분류표
mean(pred!=dia.test[,6]) #오분류율



ROC.naive = performance(prediction(as.numeric(pred), dia.train$Outcome),"tpr","fpr")
plot(ROC.naive,main="naiveBayes ROC곡선")
#

#k-근방 분류
library(class)
tune.out <- tune.knn(x=dia.train, y=as.factor(dia.train$Outcome), k=1:10)
tune.out
#k 뭘로 정할지 결정
m1=knn(dia.train,dia.test,dia.train$Outcome,k=6) 


mean(m1!=dia.test[,6]) #오분류율
table(m1,dia.test[,6]) #오분류표

#ROC
ROC.kk = performance(prediction(as.numeric(m1), dia.train$Outcome),"tpr","fpr")
plot(ROC.kk,main="k근방 분류 ROC곡선")


#- k-평균 군집법, 계층적 군집분석

library(caret)



#k정하기
library(NbClust)
nc <- NbClust(dia.train, min.nc = 2, max.nc = 15, method = "kmeans")

dia.kmeans <- kmeans(dia.train[,-6], centers = 4, iter.max = 10000)
dia.kmeans$centers
dia.train$cluster <- as.factor(dia.kmeans$cluster)##
#qplot(Pregnancies, Glucose, colour = cluster, data = dia.train)#3
plot(dia.train$BMI,dia.train$Glucose,col=dia.train$cluster)
plot(dia.train$Pregnancies,dia.train$Glucose,col=dia.train$cluster)

#points(dia.kmeans$centers,col=1:2,pch=8,cex=2)


dia.train1 <- as.data.frame(dia.train)
modFit <- train(x = dia.train1[,-6],  y = dia.train1$cluster,method = "rpart")

dia.test1 <- as.data.frame(dia.train)
testClusterPred <- predict(modFit, dia.test1) 
k=table(testClusterPred ,dia.test1$Outcome);k


#계층적 군집 분석

dist_diabetes <- dist(dia.train[,-6], method = "euclidean") #거리 계산
 dia.hclust <- hclust(dist_diabetes, method = "ward.D") #군집분석
 summary(dia.hclust) #계층적 군집분석
 plot(dia.hclust)
 library(stringr)
 
 (Predicted_Species <- cutree(dia.hclust, k=4)) #4개의 군집으로 분류
  table(Predicted_Species) #정오분류표 작성
  rect.hclust(dia.hclust, k=4)
  
  
  #Roc곡선 비교
  ##
  plot(ROC.glm,col=1,main="ROC curve 비교")
  par(new=T)
  plot(ROC.tree,col=2)
  par(new=T)
  plot(ROC.naive,col=3)
  par(new=T)
  plot(ROC.kk,col=4)
  legend(0.665,0.25,c("Logistic","의사결정나무","naiveBayes","k-근방분류"),col=1:4,fill=1:4)
  
  